import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app import database
from usagipass.app.database import async_session_ctx, partial_update_model, require_session
from usagipass.app.models import *
from usagipass.app.usecases import maimai
from usagipass.app.usecases.accounts import apply_preference
from usagipass.app.usecases.authorize import verify_user

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("")
async def update_user(user_update: UserUpdate, user: User = Depends(verify_user), session: AsyncSession = Depends(require_session)):
    user.updated_at = datetime.utcnow()
    await partial_update_model(session, user, user_update)
    await session.commit()
    return {"message": "User has been updated"}


@router.get("/profile", response_model=UserProfile)
async def get_profile(user: User = Depends(verify_user), session: AsyncSession = Depends(require_session)):
    async def prepare_preference() -> PreferencePublic:
        async with async_session_ctx() as scoped_session:
            db_preference = await scoped_session.get(UserPreference, user.username)
            if not db_preference:
                db_preference = UserPreference(username=user.username)
                await database.add_model(scoped_session, db_preference)
            preferences = PreferencePublic.model_validate(db_preference)
            await apply_preference(preferences, db_preference, scoped_session)  # apply the default images if the user has not set up
            await scoped_session.commit()
            return preferences

    # we don't wait for this task to finish, because it will take a long time
    asyncio.create_task(maimai.update_rating_passive(user.username))
    task_accounts = asyncio.create_task(session.exec(select(UserAccount).where(UserAccount.username == user.username)))
    task_wechat_accounts = asyncio.create_task(session.exec(select(WechatAccount).join(UserAccount).where(UserAccount.username == user.username)))
    task_preference = asyncio.create_task(prepare_preference())

    db_accounts, db_wechat_accounts, preferences = await asyncio.gather(task_accounts, task_wechat_accounts, task_preference)
    accounts = {account.account_server: UserAccountPublic.model_validate(account) for account in db_accounts}
    wechat_accounts = {wechat.account_name: WechatAccountPublic.model_validate(wechat) for wechat in db_wechat_accounts}
    
    api_token = user.api_token or ""
    async with async_session_ctx() as scoped_session:
        scoped_user = await scoped_session.get(User, user.username)
        if scoped_user and not scoped_user.api_token:
            api_token = uuid.uuid4().hex
            scoped_user.api_token = api_token
        await scoped_session.commit()

    user_profile = UserProfile(
        username=user.username,
        api_token=api_token,
        prefer_server=user.prefer_server,
        privilege=user.privilege,
        preferences=preferences,
        accounts=accounts,
        wechat_accounts=wechat_accounts if wechat_accounts else None,
    )
    return user_profile


@router.patch("/preference")
async def update_preference(
    preference: PreferencePublic,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    db_preference = await session.get(UserPreference, user.username)
    if not db_preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户尚未设置其偏好")
    if db_preference.username != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您不是该偏好设置的所有者")
    update_preference = PreferenceUpdate(
        **preference.model_dump(exclude={"character", "background", "frame", "passname"}),
        character_id=preference.character.id if preference.character else None,
        background_id=preference.background.id if preference.background else None,
        frame_id=preference.frame.id if preference.frame else None,
        passname_id=preference.passname.id if preference.passname else None,
    )
    user.updated_at = datetime.utcnow()
    # there's no problem with the image ids, we can update the preference
    await partial_update_model(session, db_preference, update_preference)
    await session.commit()
    return {"message": "Preference has been updated"}

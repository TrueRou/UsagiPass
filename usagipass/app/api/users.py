import asyncio
from datetime import datetime
import uuid
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status

from usagipass.app.models import *
from usagipass.app.usecases import maimai
from usagipass.app.usecases.accounts import apply_preference
from usagipass.app.usecases.authorize import verify_user
from usagipass.app.database import require_session, partial_update_model, add_model


router = APIRouter(prefix="/users", tags=["users"])


@router.patch("")
async def update_user(user_update: UserUpdate, user: User = Depends(verify_user), session: Session = Depends(require_session)):
    user.updated_at = datetime.utcnow()
    partial_update_model(session, user, user_update)
    return {"message": "User has been updated"}


@router.get("/profile", response_model=UserProfile)
async def get_profile(user: User = Depends(verify_user), session: Session = Depends(require_session)):
    db_accounts = session.exec(select(UserAccount).where(UserAccount.username == user.username)).all()
    db_preference = session.get(UserPreference, user.username)
    # we need to update the player rating if the user has not updated for 4 hours
    asyncio.ensure_future(maimai.update_rating_passive(user.username))
    if not db_preference:
        db_preference = UserPreference(username=user.username)
        add_model(session, db_preference)
    preferences = PreferencePublic.model_validate(db_preference)
    accounts = {account.account_server: UserAccountPublic.model_validate(account) for account in db_accounts}
    apply_preference(preferences, db_preference, session)  # apply the default images if the user has not set up
    if not user.api_token:
        user.api_token = uuid.uuid4().hex
        session.commit()
    user_profile = UserProfile(
        username=user.username,
        api_token=user.api_token,
        prefer_server=user.prefer_server,
        privilege=user.privilege,
        preferences=preferences,
        accounts=accounts,
    )
    return user_profile


@router.patch("/preference")
async def update_preference(
    preference: PreferencePublic,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    db_preference = session.get(UserPreference, user.username)
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
    partial_update_model(session, db_preference, update_preference)
    return {"message": "Preference has been updated"}

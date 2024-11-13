import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app import database
from app.database import require_session
from app.models.user import User, UserAccount, UserAccountPublic, UserPreference, UserPreferencePublic, UserPreferenceUpdate, UserProfile, UserUpdate
from app.models.image import Image, ImagePublic
from app.api.accounts import update_player_rating, verify_user
from config import default_character, default_background, default_frame, default_passname


router = APIRouter(prefix="/users", tags=["users"])


def apply_default(preferences: UserPreferencePublic, db_preferences: UserPreference, session: Session):
    # we need to get the image objects from the database
    character = session.get(Image, db_preferences.character_id or default_character)
    background = session.get(Image, db_preferences.background_id or default_background)
    frame = session.get(Image, db_preferences.frame_id or default_frame)
    passname = session.get(Image, db_preferences.passname_id or default_passname)
    if None in [character, background, frame, passname]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default image not found in database, please contact the administrator"
        )
    preferences.character = ImagePublic.model_validate(character)
    preferences.background = ImagePublic.model_validate(background)
    preferences.frame = ImagePublic.model_validate(frame)
    preferences.passname = ImagePublic.model_validate(passname)


@router.patch("")
async def update_user(user_update: UserUpdate, username: str = Depends(verify_user), session: Session = Depends(require_session)):
    db_user = session.get(User, username)
    database.partial_update_model(session, db_user, user_update)
    return {"message": "User has been updated"}


@router.get("/profile", response_model=UserProfile)
async def get_profile(username: str = Depends(verify_user), session: Session = Depends(require_session)):
    db_user = session.get(User, username)
    db_accounts = session.exec(select(UserAccount).where(UserAccount.username == username)).all()
    db_preference = session.get(UserPreference, username)
    prefer_account = session.exec(
        select(UserAccount).where(UserAccount.username == username, UserAccount.account_server == db_user.prefer_server)
    ).first()
    # we need to update the player rating if the user has not updated for 4 hours
    if (datetime.utcnow() - db_user.updated_at).total_seconds() >= 3600 * 4:
        asyncio.ensure_future(update_player_rating(username))
    if not db_preference:
        db_preference = database.add(session, UserPreference(username=username))
    preferences = UserPreferencePublic.model_validate(db_preference)
    accounts = {account.account_server: UserAccountPublic.model_validate(account) for account in db_accounts}
    apply_default(preferences, db_preference, session)  # apply the default images if the user has not set up
    user_profile = UserProfile(
        username=username,
        prefer_server=db_user.prefer_server,
        nickname=prefer_account.nickname,
        player_rating=prefer_account.player_rating,
        preferences=preferences,
        accounts=accounts,
    )
    return user_profile


@router.patch("/preference")
async def update_profile(
    preference: UserPreferencePublic,
    username: str = Depends(verify_user),
    session: Session = Depends(require_session),
):
    db_preference = session.get(UserPreference, username)
    if not db_preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has not set up for his preference")
    if db_preference.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this preference")
    update_preference = UserPreferenceUpdate(
        **preference.model_dump(exclude={"character", "background", "frame", "passname"}),
        character_id=preference.character.id if preference.character else None,
        background_id=preference.background.id if preference.background else None,
        frame_id=preference.frame.id if preference.frame else None,
        passname_id=preference.passname.id if preference.passname else None,
    )
    # there's no problem with the image ids, we can update the preference
    database.partial_update_model(session, db_preference, update_preference)
    return {"message": "Preference has been updated"}


@router.patch("/rating")
async def update_rating(username: str = Depends(verify_user)):
    await update_player_rating(username)

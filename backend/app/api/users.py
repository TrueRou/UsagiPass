import asyncio
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, or_, select
import bcrypt
import jwt

from app.database import async_session_ctx, require_session, async_httpx_ctx
from app.models.user import User, UserPreference, UserPreferencePublic, UserPreferenceUpdate, UserProfile
from app.models.image import Image, ImageDetail, ImagePublic
from app.maimai import scores
from app.logging import log, Ansi
from app import database
from config import jwt_secret, default_character, default_background, default_frame, default_passname


router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token", auto_error=False)


def grant_user(user: User):
    token = jwt.encode({"username": user.username}, jwt_secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def verify_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload["username"]
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user_optional(token: Annotated[str | None, Depends(optional_oauth2_scheme)]) -> str | None:
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload["username"]
    except jwt.InvalidTokenError:
        return None


async def update_player_rating(username: str):
    async with async_session_ctx() as session:
        try:
            player_rating = await scores.get_rating(username)
            user = await session.get(User, username)
            user.player_rating = player_rating
            user.updated_at = datetime.utcnow()
            await session.commit()
        except:
            log("Failed to update player rating for user: " + username, Ansi.LRED)


def apply_default(preferences: UserPreferencePublic, db_preferences: UserPreference, session: Session):
    # we need to get the image objects from the database
    character = session.get(Image, db_preferences.character_id or default_character)
    background = session.get(Image, db_preferences.background_id or default_background)
    frame = session.get(Image, db_preferences.frame_id or default_frame)
    passname = session.get(Image, db_preferences.passname_id or default_passname)
    if None in [character, background, frame]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default image not found in database, please contact the administrator"
        )
    preferences.character = ImagePublic.model_validate(character)
    preferences.background = ImagePublic.model_validate(background)
    preferences.frame = ImagePublic.model_validate(frame)
    preferences.passname = ImagePublic.model_validate(passname)
    # grant some default value here
    if not preferences.qr_size:
        preferences.qr_size = 15  # medium


@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session)):
    username = form_data.username
    password = form_data.password
    user_optional = session.exec(select(User).where(User.username == username.lower())).first()
    is_password_correct = bcrypt.checkpw(password.encode(), user_optional.hashed_password.encode()) if user_optional else False
    # user has registered in our database, we need to check the password
    if user_optional:
        # user has correct password, we can grant the token
        if is_password_correct:
            return grant_user(user_optional)
        # user has incorrect password, we need to check the diving-fish
        if not is_password_correct:
            async with async_httpx_ctx() as client:
                response = await client.post(
                    "https://www.diving-fish.com/api/maimaidxprober/login", json={"username": username, "password": password}
                )
                if "errcode" not in response.json():
                    # the password is correct, we need to update the password in our database
                    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    user_optional.hashed_password = hashed_pw
                    session.commit()
                    return grant_user(user_optional)
    # we can't verify the user in our database, we need to check the diving-fish
    if not user_optional:
        async with async_httpx_ctx() as client:
            response = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json={"username": username, "password": password})
            if "errcode" not in response.json():
                # user has logged in successfully, we need to upsert the user
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                profile = (await client.get("https://www.diving-fish.com/api/maimaidxprober/player/profile", cookies=response.cookies)).json()
                user_optional = User(username=username.lower(), hashed_password=hashed_pw, nickname=profile["nickname"], bind_qq=profile["bind_qq"])
                asyncio.ensure_future(update_player_rating(username))  # we need to update the player rating for the first time
                session.merge(user_optional)
                session.commit()
                return grant_user(user_optional)
    # we can't verify the user in our database and diving-fish
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile(username: str = Depends(verify_user), session: Session = Depends(require_session)):
    db_user = session.get(User, username)
    db_preference = session.get(UserPreference, username)
    # we need to update the player rating if the user has not updated for 4 hours
    if (datetime.utcnow() - db_user.updated_at).total_seconds() >= 3600 * 4:
        asyncio.ensure_future(update_player_rating(username))
    if not db_preference:
        db_preference = database.add(session, UserPreference(username=username))
    preferences = UserPreferencePublic.model_validate(db_preference)
    apply_default(preferences, db_preference, session)  # apply the default images if the user has not set up
    user_profile = UserProfile(**db_user.model_dump(), preferences=preferences)
    return user_profile


@router.get("/gallery", response_model=list[ImageDetail])
async def get_images(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()


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

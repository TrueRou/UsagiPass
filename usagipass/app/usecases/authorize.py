import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session


from usagipass.app.models import User
from usagipass.app.database import require_session
from usagipass.app.settings import jwt_secret


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving", auto_error=False)


def grant_user(user: User):
    token = jwt.encode({"username": user.username}, jwt_secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def verify_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(require_session)) -> User:
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return session.get(User, payload["username"])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_user_optional(token: Annotated[str | None, Depends(optional_oauth2_scheme)], session: Session = Depends(require_session)) -> User | None:
    try:
        return verify_user(token, session)
    except HTTPException:
        return None

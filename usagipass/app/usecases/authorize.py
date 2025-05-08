from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import require_session
from usagipass.app.models import Privilege, User
from usagipass.app.settings import jwt_secret

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/divingfish")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/divingfish", auto_error=False)


def grant_user(user: User):
    token = jwt.encode({"username": user.username}, jwt_secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


async def verify_admin(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(require_session)):
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if (user := await session.get(User, payload["username"])) and user.privilege == Privilege.ADMIN:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是管理员",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的身份验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(require_session)) -> User:
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if user := await session.get(User, payload["username"]):
            return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的身份验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_user_optional(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)], session: AsyncSession = Depends(require_session)
) -> User | None:
    try:
        if token and (payload := jwt.decode(token, jwt_secret, algorithms=["HS256"])):
            if user := await session.get(User, payload["username"]):
                return user
    except jwt.InvalidTokenError:
        pass

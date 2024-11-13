import asyncio
from httpx import ConnectError, ReadTimeout
import jwt
from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import async_httpx_ctx, async_session_ctx, require_session
from app.logging import Ansi, log
from app.maimai import scores
from app.models.user import AccountServer, User, UserAccount, UserPreference
from app.models.image import Image
from config import jwt_secret, lxns_developer_token


router = APIRouter(prefix="/accounts", tags=["accounts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving", auto_error=False)


def _grant_user(user: User):
    token = jwt.encode({"username": user.username}, jwt_secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


async def _update_lxns(account_name: str):
    async with async_session_ctx() as session:
        async with async_httpx_ctx() as client:
            try:
                headers = {"Authorization": lxns_developer_token}
                response_data = (await client.get("https://maimai.lxns.net/api/v0/maimai/player/" + account_name, headers=headers)).json()
                if not response_data["success"]:
                    raise Exception("Failed to fetch player data from lxns")
                account = await session.get(UserAccount, (account_name, AccountServer.LXNS))
                account.player_rating = response_data["data"]["rating"]
            except:
                log("Failed to update player rating from lxns for account: " + account_name, Ansi.LRED)


async def _update_diving(account_name: str):
    async with async_session_ctx() as session:
        try:
            player_rating = await scores.get_rating(account_name)
            account = await session.get(UserAccount, (account_name, AccountServer.DIVING_FISH))
            account.player_rating = player_rating
            account.updated_at = datetime.utcnow()
            await session.commit()
        except:
            log("Failed to update player rating from diving-fish for account: " + account_name, Ansi.LRED)


async def _dispose_user(source: str, target: str):
    async with async_session_ctx() as session:
        source_user = await session.get(User, source)
        source_accounts = await session.execute(select(UserAccount).where(UserAccount.username == source))
        source_images = await session.execute(select(Image).where(Image.uploaded_by == source))
        source_preferences = await session.get(UserPreference, source)
        target_preferences = await session.get(UserPreference, target)
        for account in source_accounts.scalars():
            await session.delete(account)
            session.expire
        for image in source_images.scalars():
            image.uploaded_by = target
        for field in UserPreference.__table__.columns:
            field_name = field.name
            source_value = getattr(source_preferences, field_name, None)
            target_value = getattr(target_preferences, field_name, None)
            if target_value is None and source_value is not None:
                setattr(target_preferences, field_name, source_value)
        await session.delete(source_preferences)
        await session.delete(source_user)
        await session.commit()


def verify_user_optional(token: Annotated[str | None, Depends(optional_oauth2_scheme)]) -> str | None:
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload["username"]
    except jwt.InvalidTokenError:
        return None


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


async def update_player_rating(username: str):
    async with async_session_ctx() as session:
        user = await session.get(User, username)
        accounts = await session.execute(select(UserAccount).where(UserAccount.username == username))
        for account in accounts.scalars():
            if account.account_server == AccountServer.DIVING_FISH:
                asyncio.ensure_future(_update_diving(account.account_name))
            if account.account_server == AccountServer.LXNS:
                asyncio.ensure_future(_update_lxns(account.account_name))
            account.updated_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await session.commit()


@router.post("/token/diving")
async def get_token_diving(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session)):
    account = session.get(UserAccount, (form_data.username, AccountServer.DIVING_FISH))

    if account and account.account_name == form_data.username and account.account_password == form_data.password:
        user = session.get(User, account.username)
        return _grant_user(user)

    async with async_httpx_ctx() as client:
        try:
            json = {"username": form_data.username, "password": form_data.password}
            response = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=json)
        except (ConnectError, ReadTimeout):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="无法连接到水鱼查分器服务",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if "errcode" not in response.json():
            profile = (await client.get("https://www.diving-fish.com/api/maimaidxprober/player/profile", cookies=response.cookies)).json()
            if not account:
                user = User(username=form_data.username.lower(), prefer_server=AccountServer.DIVING_FISH)
                account = UserAccount(
                    account_name=form_data.username,
                    account_server=AccountServer.DIVING_FISH,
                    account_password=form_data.password,
                    username=user.username,
                    nickname=profile["nickname"],
                    bind_qq=profile["bind_qq"],
                )
                session.add_all([user, account])
            else:
                account.account_password = form_data.password
                account.nickname = profile["nickname"]
                account.bind_qq = profile["bind_qq"]
            asyncio.ensure_future(_update_diving(form_data.username))
            session.commit()
            user = session.get(User, account.username)
            return _grant_user(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="水鱼查分器用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.post("/token/lxns")
async def get_token_lxns(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session)):
    personal_token = form_data.password

    account = session.exec(
        select(UserAccount).where(UserAccount.account_password == personal_token, UserAccount.account_server == AccountServer.LXNS)
    ).first()

    if account and account.account_name == form_data.username and account.account_password == form_data.password:
        user = session.get(User, account.username)
        return _grant_user(user)

    async with async_httpx_ctx() as client:
        try:
            headers = {"X-User-Token": personal_token.encode()}
            response_data = (await client.get("https://maimai.lxns.net/api/v0/user/maimai/player", headers=headers)).json()
        except (ConnectError, ReadTimeout):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="无法连接到落雪服务",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if response_data["success"]:
            account_name = str(response_data["data"]["friend_code"])
            # verify if the friend code is ok (user has not bind to maimai?)
            account = session.get(UserAccount, (account_name, AccountServer.LXNS))
            if not account:
                user = User(username=account_name, prefer_server=AccountServer.LXNS)
                account = UserAccount(
                    account_name=account_name,
                    account_server=AccountServer.LXNS,
                    account_password=personal_token,
                    username=user.username,
                    nickname=response_data["data"]["name"],
                    player_rating=response_data["data"]["rating"],
                )
                session.add_all([user, account])
                session.commit()
            user = session.get(User, account.username)
            return _grant_user(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="落雪个人 API 密钥不存在或已失效",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.post("/bind/diving")
async def bind_diving(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session), username: str = Depends(verify_user)
):
    account = session.get(UserAccount, (form_data.username, AccountServer.DIVING_FISH))
    if account and account.username == username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法重复绑定自己的账号", headers={"WWW-Authenticate": "Bearer"})
    async with async_httpx_ctx() as client:
        try:
            json = {"username": form_data.username, "password": form_data.password}
            response = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=json)
        except (ConnectError, ReadTimeout):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="无法连接到水鱼查分器服务",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if "errcode" not in response.json():
            profile = (await client.get("https://www.diving-fish.com/api/maimaidxprober/player/profile", cookies=response.cookies)).json()
            # verify if the account has been binded, if so, dispose the old account and user.
            if account:
                # dispose the old account and user, transfer the data to the new account
                await _dispose_user(account.username, username)
            new_account = UserAccount(
                account_name=form_data.username,
                account_server=AccountServer.DIVING_FISH,
                account_password=form_data.password,
                username=username,
                nickname=profile["nickname"],
                bind_qq=profile["bind_qq"],
            )
            session.merge(new_account)
            session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="水鱼查分器用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.post("/bind/lxns")
async def bind_lxns(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session), username: str = Depends(verify_user)
):
    personal_token = form_data.password
    async with async_httpx_ctx() as client:
        try:
            headers = {"X-User-Token": personal_token.encode()}
            response_data = (await client.get("https://maimai.lxns.net/api/v0/user/maimai/player", headers=headers)).json()
        except (ConnectError, ReadTimeout):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="无法连接到落雪服务",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if response_data["success"]:
            account_name = str(response_data["data"]["friend_code"])
            account = session.get(UserAccount, (account_name, AccountServer.LXNS))
            if account and account.username == username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法重复绑定自己的账号", headers={"WWW-Authenticate": "Bearer"})
            if account:
                # dispose the old account and user, transfer the data to the new account
                await _dispose_user(account.username, username)
            new_account = UserAccount(
                account_name=account_name,
                account_server=AccountServer.LXNS,
                account_password=personal_token,
                username=username,
                nickname=response_data["data"]["name"],
                player_rating=response_data["data"]["rating"],
            )
            session.merge(new_account)
            session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="落雪个人 API 密钥不存在或已失效",
                headers={"WWW-Authenticate": "Bearer"},
            )

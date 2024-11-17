import asyncio
from httpx import ConnectError, ReadTimeout
import jwt
from typing import Annotated
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import async_httpx_ctx, async_session_ctx, require_session
from app.logging import Ansi, log
from app.maimai import crawler
from app.maimai.crawler import CrawlerResult, DivingCrawler, LxnsCrawler
from app.models.user import AccountServer, User, UserAccount, UserPreference
from app.models.image import Image
from config import jwt_secret


router = APIRouter(prefix="/accounts", tags=["accounts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/token/diving", auto_error=False)


def _grant_user(user: User):
    token = jwt.encode({"username": user.username}, jwt_secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


async def _dispose_user(source: str, target: str):
    async with async_session_ctx() as session:
        source_user = await session.get(User, source)
        source_accounts = await session.execute(select(UserAccount).where(UserAccount.username == source))
        source_images = await session.execute(select(Image).where(Image.uploaded_by == source))
        source_preferences = await session.get(UserPreference, source)
        target_preferences = await session.get(UserPreference, target)
        for account in source_accounts.scalars():
            await session.delete(account)
        for image in source_images.scalars():
            image.uploaded_by = target
        for field in UserPreference.__table__.columns:
            field_name = field.name
            source_value = getattr(source_preferences, field_name, None)
            target_value = getattr(target_preferences, field_name, None)
            if target_value is None and source_value is not None:
                setattr(target_preferences, field_name, source_value)
        if source_preferences:
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


async def attempt_update_rating(username: str, hard: bool = False):
    async with async_session_ctx() as session:
        accounts = await session.execute(select(UserAccount).where(UserAccount.username == username))
        tasks = [
            (DivingCrawler if account.account_server == AccountServer.DIVING_FISH else LxnsCrawler).update_rating(session, account.account_name)
            for account in accounts.scalars()
            if datetime.utcnow() - account.updated_at > timedelta(minutes=30) or hard
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        if any(result is not None for result in results):
            log(f"Failed to update rating for user: {username}", Ansi.LRED)
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
            session.commit()
            asyncio.ensure_future(attempt_update_rating(form_data.username))
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
            asyncio.ensure_future(attempt_update_rating(account_name))
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
            asyncio.ensure_future(attempt_update_rating(username, hard=True))
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
            asyncio.ensure_future(attempt_update_rating(username, hard=True))
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="落雪个人 API 密钥不存在或已失效",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.post("/update/oauth")
async def update_prober_oauth():
    async with async_httpx_ctx() as client:
        try:
            resp = await client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
        except (ConnectError, ReadTimeout):
            raise HTTPException(status_code=503, detail="无法连接到华立 OAuth 服务", headers={"WWW-Authenticate": "Bearer"})
        if not resp.headers.get("location"):
            raise HTTPException(status_code=500, detail="华立 OAuth 服务返回不正确", headers={"WWW-Authenticate": "Bearer"})
        # example: https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx1fcecfcbd16803b1&redirect_uri=https%3A%2F%2Ftgk-wcaime.wahlap.com%2Fwc_auth%2Foauth%2Fcallback%2Fmaimai-dx%3Fr%3DINesnJ5e%26t%3D214115533&response_type=code&scope=snsapi_base&state=5E7AB78BF1B35471B7BF8DD69E6B50F4361818FA6E01FC#wechat_redirect
        return {"url": resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")}


@router.get("/update/callback", response_model=list[CrawlerResult])
async def update_prober_callback(
    r: str,
    t: str,
    code: str,
    state: str,
    username: str = Depends(verify_user),
    session: Session = Depends(require_session),
):
    params = {"r": r, "t": t, "code": code, "state": state}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
        "Host": "tgk-wcaime.wahlap.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    async with async_httpx_ctx() as client:
        try:
            resp = await client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=params, headers=headers)
            if resp.status_code != 302:
                raise TimeoutError
            resp = await client.get(resp.next_request.url, headers=headers)
            result = await crawler.crawl_async(resp.cookies, username, session)
            asyncio.ensure_future(attempt_update_rating(username, hard=True))
            return result
        except (ConnectError, ReadTimeout):
            raise HTTPException(status_code=503, detail="无法连接到华立服务器", headers={"WWW-Authenticate": "Bearer"})
        except TimeoutError:
            raise HTTPException(status_code=400, detail="华立 OAuth 已过期", headers={"WWW-Authenticate": "Bearer"})

from datetime import datetime
from httpx import ConnectError, ReadTimeout
from fastapi import HTTPException, status
from sqlmodel import Session

from usagipass.app.database import async_httpx_ctx
from usagipass.app.logging import Ansi, log
from usagipass.app.models import AccountServer, User, UserAccount
from usagipass.app.usecases.crawler import fetch_rating_retry


async def auth_divingfish(account_name: str, account_password: str) -> dict:
    async with async_httpx_ctx() as client:
        try:
            json = {"username": account_name, "password": account_password}
            response = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=json)
            if "errcode" in response.json():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="水鱼查分器用户名或密码错误")
            profile = (await client.get("https://www.diving-fish.com/api/maimaidxprober/player/profile", cookies=response.cookies)).json()
            return profile
        except (ConnectError, ReadTimeout):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="无法连接到水鱼查分器服务")


async def auth_lxns(personal_token: str) -> dict:
    async with async_httpx_ctx() as client:
        try:
            headers = {"X-User-Token": personal_token.encode()}
            response = (await client.get("https://maimai.lxns.net/api/v0/user/maimai/player", headers=headers)).json()
            if not response["success"]:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="落雪服务个人令牌错误")
            return response["data"]
        except (ConnectError, ReadTimeout):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="无法连接到落雪查分器服务")


async def merge_user(session: Session, account_name: str, server: AccountServer) -> User:
    account = session.get(UserAccount, (account_name, server))
    user = session.get(User, account.username) if account else User(username=account_name, prefer_server=server)
    user.prefer_server = server
    return session.merge(user)


async def merge_divingfish(session: Session, user: User, account_name: str, account_password: str) -> UserAccount:
    account = session.get(UserAccount, (account_name, AccountServer.DIVING_FISH))
    if account and account.username != user.username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"该水鱼账号已被其他账号 {user.username} 绑定")
    profile = await auth_divingfish(account_name, account_password)
    new_account = UserAccount(
        account_name=account_name,
        account_server=AccountServer.DIVING_FISH,
        account_password=account_password,
        username=user.username,
        nickname=profile["nickname"],
        bind_qq=profile["bind_qq"],
    )
    new_account.player_rating = await fetch_rating_retry(new_account)
    session.merge(new_account)
    return new_account


async def merge_lxns(session: Session, user: User, personal_token: str) -> UserAccount:
    profile = await auth_lxns(personal_token)
    account_name = str(profile["friend_code"])
    account = session.get(UserAccount, (account_name, AccountServer.LXNS))
    if account and account.username != user.username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"该落雪账号已被其他账号 {user.username} 绑定")
    new_account = UserAccount(
        account_name=account_name,
        account_server=AccountServer.LXNS,
        account_password=personal_token,
        username=user.username,
        nickname=profile["name"],
    )
    new_account.player_rating = await fetch_rating_retry(new_account)
    session.merge(new_account)
    return new_account

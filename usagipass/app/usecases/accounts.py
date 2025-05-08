import asyncio

from fastapi import HTTPException, status
from httpx import ConnectError, ReadTimeout
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import httpx_client
from usagipass.app.models import AccountServer, Image, ImagePublic, PreferencePublic, User, UserAccount, UserPreference
from usagipass.app.settings import default_background, default_character, default_frame, default_passname
from usagipass.app.usecases.crawler import fetch_rating_retry


async def apply_preference(preferences: PreferencePublic, db_preferences: UserPreference, session: AsyncSession):
    # we need to get the image objects from the database
    character = await session.get(Image, db_preferences.character_id or default_character)
    background = await session.get(Image, db_preferences.background_id or default_background)
    frame = await session.get(Image, db_preferences.frame_id or default_frame)
    passname = await session.get(Image, db_preferences.passname_id or default_passname)
    if None in [character, background, frame, passname]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="默认图片未在数据库中找到，请联系开发者")
    preferences.character = ImagePublic.model_validate(character)
    preferences.background = ImagePublic.model_validate(background)
    preferences.frame = ImagePublic.model_validate(frame)
    preferences.passname = ImagePublic.model_validate(passname)


async def auth_divingfish(account_name: str, account_password: str) -> dict:
    try:
        json = {"username": account_name, "password": account_password}
        response = await httpx_client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=json)
        if "errcode" in response.json():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="水鱼查分器用户名或密码错误")
        profile = (await httpx_client.get("https://www.diving-fish.com/api/maimaidxprober/player/profile", cookies=response.cookies)).json()
        return profile
    except (ConnectError, ReadTimeout):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="无法连接到水鱼查分器服务")


async def auth_lxns(personal_token: str) -> dict:
    try:
        headers = {"X-User-Token": personal_token}
        response = (await httpx_client.get("https://maimai.lxns.net/api/v0/user/maimai/player", headers=headers)).json()
        if not response["success"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="落雪服务个人令牌错误")
        return response["data"]
    except (ConnectError, ReadTimeout):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="无法连接到落雪查分器服务")


async def merge_user(session: AsyncSession, account_name: str, server: AccountServer) -> User:
    account = await session.get(UserAccount, (account_name, server))
    if account and (user := await session.get(User, account.username)):
        user.prefer_server = server
        return user
    else:
        user = User(username=account_name, prefer_server=server)
        return await session.merge(user)


async def merge_divingfish(session: AsyncSession, user: User, account_name: str, account_password: str) -> UserAccount:
    account = await session.get(UserAccount, (account_name, AccountServer.DIVING_FISH))
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
    asyncio.create_task(session.merge(new_account))
    return new_account


async def merge_lxns(session: AsyncSession, user: User, personal_token: str) -> UserAccount:
    profile = await auth_lxns(personal_token)
    account_name = str(profile["friend_code"])
    account = await session.get(UserAccount, (account_name, AccountServer.LXNS))
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
    await session.merge(new_account)
    return new_account

import asyncio
import time
import traceback
import typing
from datetime import datetime

from fastapi import HTTPException, status
from httpx import Cookies
from maimai_py import DivingFishProvider, LXNSProvider, MaimaiScores, Player, PlayerIdentifier, ScoreExtend, WechatPlayer, WechatProvider
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import retry, stop_after_attempt

from usagipass.app.database import async_session_ctx, maimai_client
from usagipass.app.logging import Ansi, log
from usagipass.app.models import AccountServer, CrawlerResult, User, UserAccount
from usagipass.app.settings import divingfish_developer_token, lxns_developer_token


async def merge_wechat(username: str, cookies: Cookies) -> UserAccount:
    async with async_session_ctx() as session:
        player = typing.cast(WechatPlayer, await maimai_client.players(PlayerIdentifier(credentials=cookies), WechatProvider()))
        account_name = str(player.friend_code)

        account = await session.get(UserAccount, (account_name, AccountServer.WECHAT))
        if account and account.username != username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"该 WECHAT 账号已被其他账号 {username} 绑定")

        new_account = UserAccount(
            account_name=account_name,
            account_server=AccountServer.WECHAT,
            account_password="",
            username=username,
            nickname=player.name,
            player_rating=player.rating,
        )
        await session.merge(new_account)
        await session.commit()

        return new_account


@retry(stop=stop_after_attempt(3), reraise=True)
async def fetch_wechat_retry(username: str, cookies: Cookies) -> MaimaiScores:
    _, scores = await asyncio.gather(
        merge_wechat(username, cookies),
        maimai_client.scores(PlayerIdentifier(credentials=cookies), provider=WechatProvider()),
    )

    return scores


@retry(stop=stop_after_attempt(3))
async def fetch_rating_retry(account: UserAccount) -> int:
    ident, provider = None, None
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(friend_code=int(account.account_name))
        provider = LXNSProvider(lxns_developer_token)
    assert ident and provider, "Invalid account server"
    player: Player = await maimai_client.players(ident, provider)
    return player.rating


@retry(stop=stop_after_attempt(3))
async def upload_server_retry(account: UserAccount, scores: list[ScoreExtend]):
    ident, provider = None, None
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name, credentials=account.account_password)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(credentials=account.account_password)
        provider = LXNSProvider(lxns_developer_token)
    assert ident and provider, "Invalid account server"
    await maimai_client.updates(ident, scores, provider)


async def fetch_wechat(username: str, cookies: Cookies) -> tuple[list[ScoreExtend], CrawlerResult]:
    try:
        scores = await fetch_wechat_retry(username, cookies)
        result = CrawlerResult(account_server=AccountServer.WECHAT, success=True, scores_num=len(scores.scores))
        return scores.scores, result
    except Exception as e:
        traceback.print_exc()
        log(f"Failed to fetch scores from wechat for {username}.", Ansi.LRED)
        return [], CrawlerResult(account_server=AccountServer.WECHAT, success=False, scores_num=0, err_msg=repr(e))


async def update_rating(account: UserAccount, result: CrawlerResult) -> CrawlerResult:
    async with async_session_ctx() as scoped_session:
        account = await scoped_session.get(UserAccount, (account.account_name, account.account_server)) or account
        result.from_rating = account.player_rating
        try:
            result.to_rating = await fetch_rating_retry(account)
            log(f"{account.username}({account.account_server.name} {account.account_name}) {result.from_rating} -> {result.to_rating})", Ansi.GREEN)
        except Exception as e:
            result.to_rating = result.from_rating
            traceback.print_exc()
            log(f"Failed to update rating for {account.username}({account.account_server.name} {account.account_name}).", Ansi.LRED)
        account.player_rating = result.to_rating
        account.updated_at = datetime.utcnow()
        await scoped_session.commit()
    return result


async def upload_server(account: UserAccount, scores: list[ScoreExtend]) -> CrawlerResult:
    try:
        begin = time.time()
        await upload_server_retry(account, scores)
        result = CrawlerResult(account_server=account.account_server, success=True, scores_num=len(scores), elapsed_time=time.time() - begin)
        return await update_rating(account, result)
    except Exception as e:
        traceback.print_exc()
        log(f"Failed to upload {account.account_server.name} for {account.username}.", Ansi.LRED)
        return CrawlerResult(account_server=account.account_server, success=False, scores_num=len(scores), err_msg=str(e))


async def crawl_async(cookies: Cookies, user: User, session: AsyncSession) -> list[CrawlerResult]:
    begin = time.time()
    accounts, wechat_results = await asyncio.gather(
        asyncio.create_task(session.exec(select(UserAccount).where(UserAccount.username == user.username))),
        asyncio.create_task(fetch_wechat(user.username, cookies)),
    )
    wechat_results[1].elapsed_time = time.time() - begin
    crawler_results = [wechat_results[1]]
    if wechat_results[1].success:
        uploads = await asyncio.gather(*[asyncio.create_task(upload_server(account, wechat_results[0])) for account in accounts])
        crawler_results.extend(uploads)
    return crawler_results

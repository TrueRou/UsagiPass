import asyncio
import time
import traceback
from datetime import datetime

from httpx import Cookies
from maimai_py import DivingFishProvider, LXNSProvider, MaimaiScores, PlayerIdentifier, WechatProvider
from maimai_py.models import Player, Score
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import retry, stop_after_attempt

from usagipass.app.database import async_session_ctx, maimai_client
from usagipass.app.logging import Ansi, log
from usagipass.app.models import AccountServer, CrawlerResult, User, UserAccount
from usagipass.app.settings import divingfish_developer_token, lxns_developer_token


@retry(stop=stop_after_attempt(3), reraise=True)
async def fetch_wechat_retry(cookies: Cookies) -> MaimaiScores:
    return await maimai_client.scores(PlayerIdentifier(credentials=cookies), provider=WechatProvider())


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
async def upload_server_retry(account: UserAccount, scores: list[Score]):
    ident, provider = None, None
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name, credentials=account.account_password)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(credentials=account.account_password)
        provider = LXNSProvider(lxns_developer_token)
    assert ident and provider, "Invalid account server"
    await maimai_client.updates(ident, scores, provider)


async def fetch_wechat(username: str, cookies: Cookies) -> tuple[list[Score], CrawlerResult]:
    try:
        scores = await fetch_wechat_retry(cookies)
        result = CrawlerResult(
            account_server=AccountServer.WECHAT,
            success=True,
            scores_num=len(scores.scores),
        )
        distinct_scores = await scores.get_distinct()
        return distinct_scores.scores, result
    except Exception as e:
        traceback.print_exc()
        log(f"Failed to fetch scores from wechat for {username}.", Ansi.LRED)
        return [], CrawlerResult(
            account_server=AccountServer.WECHAT,
            success=False,
            scores_num=0,
            err_msg=repr(e),
        )


async def update_rating(account: UserAccount, result: CrawlerResult = CrawlerResult()) -> CrawlerResult:
    async with async_session_ctx() as session:
        account = await session.get(UserAccount, (account.account_name, account.account_server)) or account
        result.from_rating = account.player_rating
        try:
            result.to_rating = await fetch_rating_retry(account)
            log(
                f"{account.username}({account.account_server.name} {account.account_name}) {result.from_rating} -> {result.to_rating})",
                Ansi.GREEN,
            )
        except Exception as e:
            result.to_rating = result.from_rating
            traceback.print_exc()
            log(
                f"Failed to update rating for {account.username}({account.account_server.name} {account.account_name}).",
                Ansi.LRED,
            )
        account.player_rating = result.to_rating
        account.updated_at = datetime.utcnow()
        await session.commit()
    return result


async def upload_server(account: UserAccount, scores: list[Score]) -> CrawlerResult:
    try:
        begin = time.time()
        await upload_server_retry(account, scores)
        return CrawlerResult(
            account_server=account.account_server,
            success=True,
            scores_num=len(scores),
            elapsed_time=time.time() - begin,
        )
    except Exception as e:
        traceback.print_exc()
        log(
            f"Failed to upload {account.account_server.name} for {account.username}.",
            Ansi.LRED,
        )
        return CrawlerResult(
            account_server=account.account_server,
            success=False,
            scores_num=len(scores),
            err_msg=str(e),
        )


async def crawl_async(cookies: Cookies, user: User, session: AsyncSession) -> list[CrawlerResult]:
    accounts = (await session.exec(select(UserAccount).where(UserAccount.username == user.username))).all()
    begin = time.time()
    scores, result = await fetch_wechat(user.username, cookies)
    result.elapsed_time = time.time() - begin
    if result.success:
        uploads = await asyncio.gather(
            *[upload_server(account, scores) for account in accounts],
            return_exceptions=False,
        )
        async with asyncio.TaskGroup() as tg:
            for account, upload in zip(accounts, uploads):
                tg.create_task(update_rating(account, upload))
        return [result, *uploads]
    return [result]

import asyncio
import time
import traceback
from httpx import Cookies
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session, select
from tenacity import retry, stop_after_attempt
from maimai_py.models import Score, Player, MaimaiScores
from maimai_py import MaimaiClient, PlayerIdentifier, WechatProvider, DivingFishProvider, LXNSProvider

from app.logging import Ansi, log
from app.database import session_ctx
from app.models.user import AccountServer, User, UserAccount
from config import lxns_developer_token, divingfish_developer_token

maimai = MaimaiClient()


class CrawlerResult(BaseModel):
    account_server: int = AccountServer.WECHAT
    success: bool = False
    scores_num: int = 0
    from_rating: int = 0
    to_rating: int = 0
    err_msg: str = ""
    elapsed_time: float = 0.0


@retry(stop=stop_after_attempt(3), reraise=True)
async def fetch_wechat_retry(cookies: Cookies) -> MaimaiScores:
    return await maimai.scores(PlayerIdentifier(credentials=cookies), provider=WechatProvider())


@retry(stop=stop_after_attempt(3))
async def fetch_rating_retry(account: UserAccount) -> int:
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(friend_code=account.account_name)
        provider = LXNSProvider(lxns_developer_token)
    player: Player = await maimai.players(ident, provider)
    return player.rating


@retry(stop=stop_after_attempt(3))
async def upload_server_retry(account: UserAccount, scores: list[Score]):
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name, credentials=account.account_password)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(credentials=account.account_password)
        provider = LXNSProvider(lxns_developer_token)
    await maimai.updates(ident, scores, provider)


async def fetch_wechat(username: str, cookies: Cookies) -> tuple[list[Score], CrawlerResult]:
    try:
        scores = await fetch_wechat_retry(cookies)
        result = CrawlerResult(account_server=AccountServer.WECHAT, success=True, scores_num=len(scores.scores))
        return scores.as_distinct.scores, result
    except Exception as e:
        log(f"Failed to fetch scores for {username}: {e}", Ansi.RED)
        log(traceback.format_exc(), Ansi.RED)
        return [], CrawlerResult(account_server=AccountServer.WECHAT, success=False, scores_num=0, err_msg=str(e))


async def fetch_rating(account: UserAccount, result: CrawlerResult = CrawlerResult()) -> CrawlerResult:
    try:
        ratings = await fetch_rating_retry(account)
        result.from_rating = account.player_rating
        result.to_rating = ratings
        return result
    except Exception as e:
        log(f"Failed to fetch rating for {account.username}: {e}", Ansi.RED)
        log(traceback.format_exc(), Ansi.RED)
        return -1


async def update_rating(account: UserAccount, result: CrawlerResult = CrawlerResult()) -> CrawlerResult:
    with session_ctx() as session:
        account = session.get(UserAccount, (account.account_name, account.account_server))
        result.from_rating = account.player_rating
        try:
            result.to_rating = await fetch_rating_retry(account)
        except Exception as e:
            result.to_rating = result.from_rating
            log(f"Failed to fetch rating for {account.username}: {e}", Ansi.RED)
            log(traceback.format_exc(), Ansi.RED)
        if result.to_rating > result.from_rating:
            account.player_rating = result.to_rating
            account.updated_at = datetime.utcnow()
            session.commit()
    return result


async def upload_server(account: UserAccount, scores: list[Score]) -> CrawlerResult:
    try:
        begin = time.time()
        await upload_server_retry(account, scores)
        return CrawlerResult(account_server=account.account_server, success=True, scores_num=len(scores), elapsed_time=time.time() - begin)
    except Exception as e:
        log(f"Failed to upload {account.account_server.name} for {account.username}: {e}", Ansi.RED)
        log(traceback.format_exc(), Ansi.RED)
        return CrawlerResult(account_server=account.account_server, success=False, scores_num=len(scores), err_msg=str(e))


async def crawl_async(cookies: Cookies, user: User, session: Session) -> list[CrawlerResult]:
    accounts = session.exec(select(UserAccount).where(UserAccount.username == user.username)).all()
    begin = time.time()
    scores, result = await fetch_wechat(user.username, cookies)
    result.elapsed_time = time.time() - begin
    if result.success:
        uploads = await asyncio.gather(*[upload_server(account, scores) for account in accounts])
        async with asyncio.TaskGroup() as tg:
            for account, upload in zip(accounts, uploads):
                tg.create_task(update_rating(account, upload))
        return [result, *uploads]
    return [result]

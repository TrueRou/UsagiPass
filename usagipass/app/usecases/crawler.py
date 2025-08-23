import asyncio
import time
import traceback
from datetime import datetime

from httpx import Cookies
from maimai_py import DivingFishProvider, LXNSProvider, MaimaiScores, Player, PlayerIdentifier, ScoreExtend, WechatProvider
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import retry, stop_after_attempt

from usagipass.app.database import async_session_ctx, maimai_client
from usagipass.app.logging import Ansi, log
from usagipass.app.models import AccountServer, CrawlerResult, User, UserAccount, WechatAccount
from usagipass.app.settings import divingfish_developer_token, lxns_developer_token


@retry(stop=stop_after_attempt(3), reraise=True)
async def fetch_wechat_retry(cookies: Cookies) -> MaimaiScores:
    return await maimai_client.scores(PlayerIdentifier(credentials=cookies), provider=WechatProvider())


@retry(stop=stop_after_attempt(3), reraise=True)
async def fetch_wahlap_player_retry(cookies: Cookies) -> Player:
    return await maimai_client.players(PlayerIdentifier(credentials=cookies), provider=WechatProvider())


@retry(stop=stop_after_attempt(3))
async def fetch_rating_retry(account: UserAccount) -> int:
    ident, provider = None, None
    if account.account_server == AccountServer.DIVING_FISH:
        ident = PlayerIdentifier(username=account.account_name)
        provider = DivingFishProvider(divingfish_developer_token)
    elif account.account_server == AccountServer.LXNS:
        ident = PlayerIdentifier(friend_code=int(account.account_name))
        provider = LXNSProvider(lxns_developer_token)
    elif account.account_server == AccountServer.WECHAT:
        # WECHAT 账户的 rating 由华立服务器提供，无需额外获取
        return account.player_rating
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
    elif account.account_server == AccountServer.WECHAT:
        # WECHAT 账户不支持成绩上传
        return
    assert ident and provider, "Invalid account server"
    await maimai_client.updates(ident, scores, provider)


async def fetch_wechat(username: str, cookies: Cookies) -> tuple[list[ScoreExtend], CrawlerResult]:
    try:
        scores = await fetch_wechat_retry(cookies)
        result = CrawlerResult(account_server=AccountServer.WECHAT, success=True, scores_num=len(scores.scores))
        return scores.scores, result
    except Exception as e:
        traceback.print_exc()
        log(f"Failed to fetch scores from wechat for {username}.", Ansi.LRED)
        return [], CrawlerResult(account_server=AccountServer.WECHAT, success=False, scores_num=0, err_msg=repr(e))


async def create_wechat_account(username: str, cookies: Cookies, session: AsyncSession) -> tuple[UserAccount, WechatAccount] | None:
    """创建 WECHAT 账户，基于华立玩家信息"""
    try:
        player = await fetch_wahlap_player_retry(cookies)
        
        # 导入 accounts 模块避免循环导入
        from usagipass.app.usecases.accounts import merge_wechat
        
        # 获取用户对象
        user = await session.get(User, username)
        if not user:
            log(f"User {username} not found when creating WECHAT account", Ansi.LRED)
            return None
        
        # 准备玩家数据
        player_data = {
            "name": player.name,
            "rating": player.rating,
            "friend_code": getattr(player, 'friend_code', 0),
            "star": getattr(player, 'star', 0),
            "trophy": getattr(player, 'trophy', None),
            "token": getattr(player, 'token', None),
        }
        
        # 创建 WECHAT 账户
        account, wechat_account = await merge_wechat(session, user, cookies, player_data)
        await session.commit()
        
        log(f"Created WECHAT account for {username}: {player.name} (FC: {player_data['friend_code']})", Ansi.GREEN)
        return account, wechat_account
        
    except Exception as e:
        traceback.print_exc()
        log(f"Failed to create WECHAT account for {username}: {str(e)}", Ansi.LRED)
        return None


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
    
    # 首先获取微信成绩数据
    wechat_scores, wechat_result = await fetch_wechat(user.username, cookies)
    wechat_result.elapsed_time = time.time() - begin
    crawler_results = [wechat_result]
    
    if wechat_result.success:
        # 创建或更新 WECHAT 账户
        wechat_account_info = await create_wechat_account(user.username, cookies, session)
        
        # 获取用户的其他账户（DIVING_FISH, LXNS）
        accounts = await session.exec(select(UserAccount).where(
            UserAccount.username == user.username,
            UserAccount.account_server != AccountServer.WECHAT
        ))
        
        # 上传成绩到其他查分器
        upload_tasks = [asyncio.create_task(upload_server(account, wechat_scores)) for account in accounts]
        uploads = await asyncio.gather(*upload_tasks)
        crawler_results.extend(uploads)
        
        # 如果成功创建了 WECHAT 账户，添加对应的结果
        if wechat_account_info:
            wechat_account, _ = wechat_account_info
            wechat_upload_result = CrawlerResult(
                account_server=AccountServer.WECHAT,
                success=True,
                scores_num=len(wechat_scores),
                from_rating=0,
                to_rating=wechat_account.player_rating,
                elapsed_time=0.0
            )
            crawler_results.append(wechat_upload_result)
    
    return crawler_results

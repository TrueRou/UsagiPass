import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from httpx import ConnectError, ReadTimeout
from sqlmodel.ext.asyncio.session import AsyncSession
from maimai_py import PlayerIdentifier, WechatProvider

from usagipass.app.database import httpx_client, require_session, maimai_client
from usagipass.app.models import AccountServer, User
from usagipass.app.usecases import accounts, authorize, crawler, maimai
from usagipass.app.usecases.authorize import verify_user
from usagipass.app.usecases.crawler import CrawlerResult

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/token/divingfish")
async def get_token_divingfish(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(require_session)):
    account_name = form_data.username
    if await accounts.auth_divingfish(account_name, form_data.password):
        user = await accounts.merge_user(session, account_name, AccountServer.DIVING_FISH)
        await accounts.merge_divingfish(session, user, account_name, form_data.password)
        await session.commit()
        return authorize.grant_user(user)


@router.post("/token/lxns")
async def get_token_lxns(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(require_session)):
    personal_token = form_data.password
    if profile := await accounts.auth_lxns(personal_token):
        account_name = str(profile["friend_code"])
        user = await accounts.merge_user(session, account_name, AccountServer.LXNS)
        await accounts.merge_lxns(session, user, personal_token)
        await session.commit()
        return authorize.grant_user(user)


@router.post("/bind/divingfish")
async def bind_diving(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(require_session), user: User = Depends(verify_user)
):
    await accounts.merge_divingfish(session, user, form_data.username, form_data.password)
    asyncio.create_task(maimai.update_rating_passive(user.username))
    await session.commit()


@router.post("/bind/lxns")
async def bind_lxns(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(require_session), user: User = Depends(verify_user)
):
    personal_token = form_data.password
    await accounts.merge_lxns(session, user, personal_token)
    asyncio.create_task(maimai.update_rating_passive(user.username))
    await session.commit()


@router.post("/update/oauth")
async def update_prober_oauth():
    try:
        resp = await httpx_client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
    except (ConnectError, ReadTimeout):
        raise HTTPException(status_code=503, detail="无法连接到华立 OAuth 服务", headers={"WWW-Authenticate": "Bearer"})
    if not resp.headers.get("location"):
        raise HTTPException(status_code=500, detail="华立 OAuth 服务返回的响应不正确", headers={"WWW-Authenticate": "Bearer"})
    # example: https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx1fcecfcbd16803b1&redirect_uri=https%3A%2F%2Ftgk-wcaime.wahlap.com%2Fwc_auth%2Foauth%2Fcallback%2Fmaimai-dx%3Fr%3DINesnJ5e%26t%3D214115533&response_type=code&scope=snsapi_base&state=5E7AB78BF1B35471B7BF8DD69E6B50F4361818FA6E01FC#wechat_redirect
    return {"url": resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")}


@router.get("/update/callback", response_model=list[CrawlerResult])
async def update_prober_callback(
    r: str,
    t: str,
    code: str,
    state: str,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    params = {"r": r, "t": t, "code": code, "state": state}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
        "Host": "tgk-wcaime.wahlap.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    try:
        resp = await httpx_client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=params, headers=headers)
        if resp.status_code == 302 and resp.next_request:
            resp = await httpx_client.get(resp.next_request.url, headers=headers)
            results = await crawler.crawl_async(resp.cookies, user, session)
            return results
        raise HTTPException(status_code=400, detail="华立 OAuth 已过期或无效", headers={"WWW-Authenticate": "Bearer"})
    except (ConnectError, ReadTimeout):
        raise HTTPException(status_code=503, detail="无法连接到华立服务器", headers={"WWW-Authenticate": "Bearer"})


@router.get("/friends")
async def get_friends(
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    """获取用户的所有好友列表"""
    # 获取用户的微信账户信息
    wechat_account = await accounts.get_user_account(session, user.username, AccountServer.WECHAT)
    if not wechat_account:
        raise HTTPException(status_code=400, detail="未绑定微信账户，请先更新查分器以绑定微信账户")
    
    try:
        # 在实际实现中，这里需要使用存储的 cookies 来调用 maimai.py 的 get_friends 功能
        # 由于 cookies 管理比较复杂，这里先返回一个示例数据结构供前端测试
        
        # TODO: 实现真正的好友获取逻辑
        # from maimai_py import PlayerIdentifier, WechatProvider
        # cookies = # 从某处获取用户的 cookies
        # friends = await maimai_client.get_friends(PlayerIdentifier(credentials=cookies), WechatProvider())
        
        # 模拟好友数据供测试
        mock_friends = [
            {
                "id": "friend_001",
                "name": "测试好友1",
                "friend_code": "123456789012345",
                "rating": 12500,
                "icon_id": "001",  # 可能的头像ID
                "plate_id": "001",  # 可能的姓名框ID  
                "frame_id": "001",  # 可能的背景ID
                "is_opponent": False
            },
            {
                "id": "friend_002", 
                "name": "测试好友2",
                "friend_code": "123456789012346",
                "rating": 13200,
                "icon_id": "002",
                "plate_id": "002", 
                "frame_id": "002",
                "is_opponent": True
            }
        ]
        
        return {"friends": mock_friends, "message": "获取好友列表成功（当前为测试数据）"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取好友列表失败: {str(e)}")


@router.post("/friends/{friend_id}/opponent")
async def set_friend_as_opponent(
    friend_id: str,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    """设置好友为对手"""
    wechat_account = await accounts.get_user_account(session, user.username, AccountServer.WECHAT)
    if not wechat_account:
        raise HTTPException(status_code=400, detail="未绑定微信账户")
    
    try:
        # TODO: 实现真正的设置对手逻辑
        # from maimai_py import PlayerIdentifier, WechatProvider
        # cookies = # 从某处获取用户的 cookies  
        # await maimai_client.set_opponent(PlayerIdentifier(credentials=cookies), friend_id, WechatProvider())
        
        # 目前只返回成功消息
        return {"success": True, "message": f"已设置好友 {friend_id} 为对手（测试模式）"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置对手失败: {str(e)}")


@router.delete("/friends/{friend_id}/opponent")
async def cancel_friend_as_opponent(
    friend_id: str,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    """取消好友的对手设置"""
    wechat_account = await accounts.get_user_account(session, user.username, AccountServer.WECHAT)
    if not wechat_account:
        raise HTTPException(status_code=400, detail="未绑定微信账户")
    
    try:
        # TODO: 实现真正的取消对手逻辑
        # from maimai_py import PlayerIdentifier, WechatProvider
        # cookies = # 从某处获取用户的 cookies
        # await maimai_client.cancel_opponent(PlayerIdentifier(credentials=cookies), friend_id, WechatProvider())
        
        # 目前只返回成功消息
        return {"success": True, "message": f"已取消好友 {friend_id} 的对手设置（测试模式）"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消对手失败: {str(e)}")

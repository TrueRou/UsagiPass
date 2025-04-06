import asyncio
from typing import Annotated
from sqlmodel import Session
from httpx import ConnectError, ReadTimeout
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from usagipass.app.usecases import crawler
from usagipass.app.usecases.crawler import CrawlerResult
from usagipass.app.database import async_httpx_ctx, require_session
from usagipass.app.models import AccountServer, User
from usagipass.app.usecases import accounts, authorize, maimai
from usagipass.app.usecases.authorize import verify_user


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/token/divingfish")
async def get_token_divingfish(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session)):
    account_name = form_data.username
    if await accounts.auth_divingfish(account_name, form_data.password):
        user = accounts.merge_user(session, account_name, AccountServer.DIVING_FISH)
        await accounts.merge_divingfish(session, user, account_name, form_data.password)
        session.commit()
        return authorize.grant_user(user)


@router.post("/token/lxns")
async def get_token_lxns(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session)):
    personal_token = form_data.password
    if profile := await accounts.auth_lxns(personal_token):
        account_name = str(profile["friend_code"])
        user = accounts.merge_user(session, account_name, AccountServer.LXNS)
        await accounts.merge_lxns(session, user, personal_token)
        session.commit()
        return authorize.grant_user(user)


@router.post("/bind/divingfish")
async def bind_diving(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session), user: User = Depends(verify_user)
):
    await accounts.merge_divingfish(session, user, form_data.username, form_data.password)
    asyncio.ensure_future(maimai.update_rating_passive(user.username))
    session.commit()


@router.post("/bind/lxns")
async def bind_lxns(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(require_session), user: User = Depends(verify_user)
):
    personal_token = form_data.password
    await accounts.merge_lxns(session, user, personal_token)
    asyncio.ensure_future(maimai.update_rating_passive(user.username))
    session.commit()


@router.post("/update/oauth")
async def update_prober_oauth():
    async with async_httpx_ctx() as client:
        try:
            resp = await client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
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
            if resp.status_code == 302 and resp.next_request:
                resp = await client.get(resp.next_request.url, headers=headers)
                results = await crawler.crawl_async(resp.cookies, user, session)
                return results
            raise HTTPException(status_code=400, detail="华立 OAuth 已过期或无效", headers={"WWW-Authenticate": "Bearer"})
        except (ConnectError, ReadTimeout):
            raise HTTPException(status_code=503, detail="无法连接到华立服务器", headers={"WWW-Authenticate": "Bearer"})

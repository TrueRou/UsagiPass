import asyncio
from datetime import datetime
import functools
import json
import operator
import random
import re
import traceback
from typing import Any

from httpx import Cookies
from pydantic import BaseModel
from sqlmodel import Session, select
from tenacity import RetryError, retry, stop_after_attempt
from app.database import async_httpx_ctx
from app.models.user import AccountServer, UserAccount
from app.logging import Ansi, log
from app.maimai.scores import get_music_list, get_rating
from app.models.crawler import CrawlerHistory
from config import lxns_developer_token

diff_list = ["Basic", "Advanced", "Expert", "Master", "Re:Master"]
type_dict = {"SD": "standard", "DX": "dx"}


class CrawlerResult(BaseModel):
    account_server: int
    diff_label: str
    success: bool
    scores_num: int


class DivingCrawler:
    def label() -> str:
        return "Diving-Fish"

    @retry(reraise=False, stop=stop_after_attempt(3))
    async def upload_scores(diving_json: Any, username: str, password: str, diff: str) -> CrawlerResult:
        async with async_httpx_ctx() as client:
            login_json = {"username": username, "password": password}
            resp1 = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=login_json)
            resp1.raise_for_status()
            resp2 = await client.post("https://www.diving-fish.com/api/maimaidxprober/player/update_records", json=diving_json, cookies=resp1.cookies)  # type: ignore
            resp2.raise_for_status()
            return CrawlerResult(account_server=AccountServer.DIVING_FISH, diff_label=diff, success=True, scores_num=len(diving_json))

    @retry(reraise=False, stop=stop_after_attempt(3))
    async def update_rating(session: Session, account_name: str):
        player_rating = await get_rating(account_name)
        account = await session.get(UserAccount, (account_name, AccountServer.DIVING_FISH))
        account.player_rating = player_rating
        account.updated_at = datetime.utcnow()
        log(f"Updated rating for user {account_name}({DivingCrawler.label()}) to {player_rating}.", Ansi.LGREEN)


class LxnsCrawler:
    def label() -> str:
        return "LXNS"

    @retry(reraise=False, stop=stop_after_attempt(5))
    async def upload_scores(diving_json: Any, username: str, password: str, diff: str) -> CrawlerResult:
        music_list = get_music_list()
        lxns_json = {
            "scores": [
                {
                    "id": music.id_lxns,
                    "type": type_dict[score["type"]] if int(music.id) < 100000 else "utage",
                    "level_index": score["level_index"],
                    "achievements": score["achievements"],
                    "dx_score": score["dxScore"],
                    "fc": score["fc"] if score["fc"] != "" else None,
                    "fs": score["fs"] if score["fs"] != "" else None,
                    "play_time": None,
                }
                for score in diving_json
                if (music := music_list.by_title(score["title"])) and music.id
            ]
        }
        async with async_httpx_ctx() as client:
            headers = {"X-User-Token": password.encode()}
            resp = await client.post("https://maimai.lxns.net/api/v0/user/maimai/player/scores", json=lxns_json, headers=headers)
            resp.raise_for_status()
            return CrawlerResult(account_server=AccountServer.LXNS, diff_label=diff, success=True, scores_num=len(lxns_json["scores"]))

    @retry(reraise=False, stop=stop_after_attempt(5))
    async def update_rating(session: Session, account_name: str):
        async with async_httpx_ctx() as client:
            headers = {"Authorization": lxns_developer_token}
            response_data = (await client.get("https://maimai.lxns.net/api/v0/maimai/player/" + account_name, headers=headers)).json()
            if not response_data["success"]:
                raise Exception("Failed to fetch player data from lxns")
            account = await session.get(UserAccount, (account_name, AccountServer.LXNS))
            account.player_rating = response_data["data"]["rating"]
            account.updated_at = datetime.utcnow()
            log(f"Updated rating for user {account_name}({LxnsCrawler.label()}) to {account.player_rating}.", Ansi.LGREEN)


async def upload_server(account: UserAccount, diving_json: Any, diff: str, session: Session) -> CrawlerResult:
    crawler = DivingCrawler if account.account_server == AccountServer.DIVING_FISH else LxnsCrawler
    if not account.account_password or account.account_password == "":
        log(f"User {account.username}({crawler.label()}) has no password saved, skipping.", Ansi.LYELLOW)
        return CrawlerResult(account_server=account.account_server, diff_label=diff, success=False, scores_num=0)
    try:
        exc_stack = None
        results = await crawler.upload_scores(diving_json, account.account_name, account.account_password, diff)
        log(f"Uploaded {diff} diff scores for user {account.username}({crawler.label()}).", Ansi.LGREEN)
    except Exception as e:
        exc_stack = traceback.format_exc()
        results = CrawlerResult(account_server=account.account_server, diff_label=diff, success=False, scores_num=0)
        log(f"Failed to upload {diff} diff scores for for user {account.username}({crawler.label()}): {str(e)}.", Ansi.LRED)
    history = CrawlerHistory(
        game_name="maimai",
        username=account.username,
        account_server=account.account_server,
        diff_label=diff,
        success=results.success,
        scores_num=results.scores_num,
        parsed_json=json.dumps(diving_json, ensure_ascii=False),
        exc_stack=exc_stack,
    )
    session.add(history)
    return results


@retry(reraise=False, stop=stop_after_attempt(3))
async def crawl_diff(diff: int, cookies: Cookies, accounts: list[UserAccount], session: Session) -> list[CrawlerResult]:
    async with async_httpx_ctx() as client:
        await asyncio.sleep(random.randint(0, 200) / 1000)  # sleep for a random amount of time between 0 and 200ms
        resp1 = await client.get(f"https://maimai.wahlap.com/maimai-mobile/record/musicGenre/search/?genre=99&diff={diff}", cookies=cookies)
        body = re.search(r"<html.*?>([\s\S]*?)</html>", resp1.text).group(1).replace(r"\s+", " ")
        # we use diving fish page parser to parse the html to readable json format
        diving_json = (await client.post("http://8.138.164.51:8089/page", headers={"content-type": "text/plain"}, content=body)).json()
        tasks = [upload_server(account, diving_json, diff_list[diff], session) for account in accounts]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def crawl_async(cookies: Cookies, username: str, session: Session) -> list[CrawlerResult]:
    accounts = session.exec(select(UserAccount).where(UserAccount.username == username)).all()
    tasks = [crawl_diff(diff, cookies, accounts, session) for diff in [0, 1, 2, 3, 4]]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    results = [result for result in results if not isinstance(result, RetryError)]
    session.commit()
    return functools.reduce(operator.concat, results, [])

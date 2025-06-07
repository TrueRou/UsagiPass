from asyncio import TaskGroup
from datetime import datetime, timedelta

from sqlmodel import select

from usagipass.app.database import async_session_ctx
from usagipass.app.models import CrawlerResult, UserAccount
from usagipass.app.usecases import crawler


# attempt to refresh the usagipass user's rating depends on check_delta
async def update_rating_passive(username: str):
    async with async_session_ctx() as scoped_session:
        accounts = await scoped_session.exec(select(UserAccount).where(UserAccount.username == username))
        async with TaskGroup() as tg:
            for account in accounts:
                if datetime.utcnow() - account.updated_at > timedelta(minutes=30):
                    tg.create_task(crawler.update_rating(account, CrawlerResult()))

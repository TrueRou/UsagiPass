import asyncio
from datetime import datetime, timedelta
from sqlmodel import select
from app.database import async_session_ctx
from app.models.user import UserAccount
from app.usecases import crawler


async def update_rating_passive(username: str):
    async with async_session_ctx() as session:
        accounts = await session.execute(select(UserAccount).where(UserAccount.username == username))
        async with asyncio.TaskGroup() as tg:
            for account in accounts.scalars():
                if datetime.utcnow() - account.updated_at > timedelta(minutes=30):
                    tg.create_task(crawler.update_rating(account))

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from usagipass.app.database import maimai_client

scheduler = AsyncIOScheduler()


async def init_sched():
    asyncio.create_task(maimai_client.songs())
    scheduler.add_job(maimai_client.flush, "cron", hour=0, minute=0, id=f"flush_mpy", replace_existing=True)
    scheduler.start()

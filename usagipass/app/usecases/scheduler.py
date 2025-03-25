import asyncio
from collections import deque
from datetime import datetime, timedelta
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from usagipass.app import settings
from usagipass.app.database import session_ctx, maimai_client, scheduler
from usagipass.app.models import CardAccount
from usagipass.app.usecases import maimai


# scheduler process applied to individual users
async def process_sched(user_ids: deque[int]):
    if len(user_ids) != 0:
        user_id = user_ids.pop()
        asyncio.ensure_future(maimai.update_scores(user_id))
        user_ids.appendleft(user_id)


# calculate the interval for the scheduler
async def calculate_sched(user_ids: deque[int], period: str) -> int:
    # calculate the total intervals in minutes
    minutes = sum(
        (int(end) - int(start) + (24 if int(end) < int(start) else 0)) * 60
        for start, end in (time_range.split("-") for time_range in period.split(","))
    )
    # clamp intervals between 1 and 15 minutes
    intervals = minutes // max(len(user_ids), 1)
    return min(max(intervals, 1), 15)


# reschedule the cron job depends on job arguments
async def update_sched(job_args: tuple[str, SelectOfScalar[CardAccount]]) -> None:
    period, select_stmt = job_args
    with session_ctx() as session:
        players = session.exec(select_stmt.order_by(CardAccount.last_updated_at.desc()))
        user_ids = deque([player.id for player in players])
    interval = await calculate_sched(user_ids, period)
    scheduler.add_job(process_sched, trigger="cron", args=[user_ids], hour=period, minute=f"*/{interval}", id=period, replace_existing=True)


# update the scheduler for active and inactive users
async def update_sched_hourly():
    threshold = timedelta(hours=settings.refresh_hour_threshold)
    job_args = [
        (settings.refresh_hour_active, select(CardAccount).where(CardAccount.last_activity_at + threshold > datetime.now())),
        (settings.refresh_hour_inactive, select(CardAccount).where(CardAccount.last_activity_at + threshold <= datetime.now())),
    ]
    async with asyncio.TaskGroup() as tg:
        [tg.create_task(update_sched(args)) for args in job_args]


async def init_sched():
    asyncio.create_task(maimai_client.songs(alias_provider=None, curve_provider=None))
    scheduler.add_job(maimai_client.flush, "cron", hour=0, minute=0)
    # scheduler.add_job(update_sched_hourly, "interval", hours=1)
    scheduler.start()

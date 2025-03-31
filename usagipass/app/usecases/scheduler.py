import asyncio
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from sqlmodel import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from usagipass.app import database
from usagipass.app.models import Card, Task, TaskStatus
from usagipass.app.logging import log, Ansi
from usagipass.app.database import session_ctx, maimai_client
from usagipass.app.usecases import browser

scheduler = AsyncIOScheduler()

tasks_folder = Path.cwd() / ".data" / "tasks"
tasks_folder.mkdir(exist_ok=True)


async def process_screenshot_task(task_id: str):
    with session_ctx() as session:
        task = session.get(Task, task_id)
        task.status = TaskStatus.RUNNING
        session.commit()
        try:
            params = json.loads(task.params)
            uuids = params.get("uuids", [])
            if cards := session.exec(select(Card).where(Card.uuid.in_(uuids))).all():
                _, zip_file = await browser.capture_card_screenshot_batch(cards)
                result_path = tasks_folder / f"{task.id}.zip"
                shutil.copy(zip_file, result_path)
            task.status = TaskStatus.COMPLETED
            task.result_path = str(result_path)
            task.updated_at = datetime.utcnow()
            session.commit()
            log(f"Task {task_id} completed successfully", Ansi.LGREEN)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            session.commit()
            log(f"Task {task_id} failed: {str(e)}", Ansi.RED)


async def create_screenshot_task(uuids: list[str], username: str) -> Task:
    with session_ctx() as session:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, task_type="screenshot_batch", params=json.dumps({"uuids": uuids}), created_by=username)
        database.add_model(session, task)
        scheduler.add_job(process_screenshot_task, args=[task_id], id=f"task_{task_id}", replace_existing=True)
        log(f"Created screenshot task {task_id} for {len(uuids)} cards", Ansi.LCYAN)
        return task


async def init_sched():
    asyncio.create_task(maimai_client.songs(alias_provider=None, curve_provider=None))
    scheduler.add_job(maimai_client.flush, "cron", hour=0, minute=0, id=f"flush_mpy", replace_existing=True)
    scheduler.start()

import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, select
from fastapi.responses import FileResponse

from usagipass.app.database import require_session
from usagipass.app.models import Card, Task, TaskPublic, TaskStatus, User
from usagipass.app.usecases.authorize import verify_admin, verify_user
from usagipass.app.usecases import scheduler

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskPublic], dependencies=[Depends(verify_admin)])
async def get_tasks(
    session: Session = Depends(require_session),
    user: User = Depends(verify_user),
):
    user_tasks = session.exec(select(Task).where(Task.created_by == user.username).order_by(col(Task.created_at).desc())).all()
    return [TaskPublic.model_validate(task) for task in user_tasks]


@router.get("/{task_id}", response_model=TaskPublic, dependencies=[Depends(verify_admin)])
async def get_task(
    task_id: str,
    session: Session = Depends(require_session),
    user: User = Depends(verify_user),
):
    if (task := session.get(Task, task_id)) and task.created_by == user.username:
        return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")


@router.get("/{task_id}/download", dependencies=[Depends(verify_admin)])
async def download_task_result(
    task_id: str,
    session: Session = Depends(require_session),
    user: User = Depends(verify_user),
):
    task = session.get(Task, task_id)
    if not task or task.created_by != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")
    if task.status != TaskStatus.COMPLETED or not task.result_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="任务结果不可用")
    return FileResponse(task.result_path, media_type="application/zip", filename=f"task_{task.id}.zip")


@router.post("/screenshots", response_model=TaskPublic, dependencies=[Depends(verify_admin)])
async def create_screenshots_task(
    uuids: List[str],
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    cards = session.exec(select(Card).where(col(Card.uuid).in_(uuids))).all()
    if len(cards) != len(uuids):
        lost_uuids = set(uuids) - {card.uuid for card in cards}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"未找到卡片: {', '.join(lost_uuids)}")
    return await scheduler.create_screenshot_task(uuids, user.username)


@router.delete("/{task_id}", dependencies=[Depends(verify_admin)])
async def delete_task(
    task_id: str,
    session: Session = Depends(require_session),
    user: User = Depends(verify_user),
):
    task = session.get(Task, task_id)
    if not task or task.created_by != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")

    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有已完成的任务可以删除")

    if task.result_path and os.path.exists(task.result_path):
        Path(task.result_path).unlink(missing_ok=True)

    session.delete(task)
    session.commit()

    return {"message": "任务删除成功"}

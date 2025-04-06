from datetime import datetime
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, status

from usagipass.app.models import Announcement, AnnouncementPublic, AnnouncementCreate, AnnouncementRead, AnnouncementUpdate, User, Privilege
from usagipass.app.usecases.authorize import verify_user
from usagipass.app.database import require_session, add_model, partial_update_model

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.post("", response_model=AnnouncementPublic, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement: AnnouncementCreate,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以创建公告")

    new_announcement = Announcement(**announcement.model_dump())
    add_model(session, new_announcement)
    return new_announcement


@router.get("", response_model=list[AnnouncementPublic])
async def list_announcements(
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    announcements = session.exec(select(Announcement)).all()

    # 检查每个公告是否已读
    result = []
    for announcement in announcements:
        read_record = session.exec(
            select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement.id, AnnouncementRead.username == user.username)
        ).first()

        announcement_public = AnnouncementPublic(**announcement.model_dump(), is_read=bool(read_record))
        result.append(announcement_public)

    return result


@router.get("/{announcement_id}", response_model=AnnouncementPublic)
async def get_announcement(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    # 检查是否已读
    read_record = session.exec(
        select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id, AnnouncementRead.username == user.username)
    ).first()

    return AnnouncementPublic(**announcement.model_dump(), is_read=bool(read_record))


@router.patch("/{announcement_id}", response_model=AnnouncementPublic)
async def update_announcement(
    announcement_id: int,
    announcement_update: AnnouncementUpdate,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以更新公告")

    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    announcement.updated_at = datetime.utcnow()
    partial_update_model(session, announcement, announcement_update)

    return AnnouncementPublic(**announcement.model_dump(), is_read=False)  # 修改后重置为未读状态


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以删除公告")

    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    session.delete(announcement)
    session.commit()


@router.post("/{announcement_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_announcement_as_read(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: Session = Depends(require_session),
):
    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    # 检查是否已经标记为已读
    read_record = session.exec(
        select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id, AnnouncementRead.username == user.username)
    ).first()

    if not read_record:
        read_record = AnnouncementRead(
            announcement_id=announcement_id,
            username=user.username,
        )
        add_model(session, read_record)

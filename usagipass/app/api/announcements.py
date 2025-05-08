from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import add_model, partial_update_model, require_session
from usagipass.app.models import Announcement, AnnouncementCreate, AnnouncementPublic, AnnouncementRead, AnnouncementUpdate, Privilege, User
from usagipass.app.usecases.authorize import verify_user

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.post("", response_model=AnnouncementPublic, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement: AnnouncementCreate,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以创建公告")

    new_announcement = Announcement(**announcement.model_dump())
    await add_model(session, new_announcement)
    await session.commit()
    return new_announcement


@router.get("", response_model=list[AnnouncementPublic])
async def list_announcements(
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    announcements = await session.exec(select(Announcement))

    result = []
    for announcement in announcements:
        clause = select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement.id, AnnouncementRead.username == user.username)
        read_record = (await session.exec(clause)).first()

        announcement_public = AnnouncementPublic(**announcement.model_dump(), is_read=bool(read_record))
        result.append(announcement_public)

    return result


@router.get("/{announcement_id}", response_model=AnnouncementPublic)
async def get_announcement(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    announcement = await session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    clause = select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id, AnnouncementRead.username == user.username)
    read_record = (await session.exec(clause)).first()

    return AnnouncementPublic(**announcement.model_dump(), is_read=bool(read_record))


@router.patch("/{announcement_id}", response_model=AnnouncementPublic)
async def update_announcement(
    announcement_id: int,
    announcement_update: AnnouncementUpdate,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以更新公告")
    announcement = await session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    announcement.updated_at = datetime.utcnow()
    await partial_update_model(session, announcement, announcement_update)
    await session.commit()

    return AnnouncementPublic(**announcement.model_dump(), is_read=False)  # 修改后重置为未读状态


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    if user.privilege != Privilege.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以删除公告")

    announcement = await session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    await session.delete(announcement)
    await session.commit()


@router.post("/{announcement_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_announcement_as_read(
    announcement_id: int,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
):
    announcement = session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    clause = select(AnnouncementRead).where(AnnouncementRead.announcement_id == announcement_id, AnnouncementRead.username == user.username)
    read_record = (await session.exec(clause)).first()

    if not read_record:
        read_record = AnnouncementRead(
            announcement_id=announcement_id,
            username=user.username,
        )
        await add_model(session, read_record)
    await session.commit()

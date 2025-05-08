from fastapi import APIRouter, Depends
from sqlmodel import col, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import require_session
from usagipass.app.models import Image, ImagePublic, User, image_kinds
from usagipass.app.usecases import authorize

router = APIRouter(tags=["servers"])


@router.get("/kinds")
async def get_kinds():
    return image_kinds


@router.get("/bits", response_model=list[ImagePublic])
async def get_images(user: User | None = Depends(authorize.verify_user_optional), session: AsyncSession = Depends(require_session)):
    clause = (
        select(Image).where(Image.uploaded_by == None).order_by(col(Image.uploaded_at).desc())
        if user is None
        else select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user.username)).order_by(col(Image.uploaded_at).desc())
    )
    return await session.exec(clause)

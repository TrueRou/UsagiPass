from fastapi import APIRouter, Depends
from sqlmodel import Session, or_, select

from app.models.server import ServerMessage
from app.maimai import kinds
from app.database import require_session
from app.models.image import Image, ImageDetail
from app.api.accounts import verify_user_optional
import config


router = APIRouter(tags=["servers"])


@router.get("/motd")
async def get_motd():
    return ServerMessage(
        maimai_version=config.maimai_version,
        server_motd=config.server_motd,
        author_motd=config.author_motd,
    )


@router.get("/kinds")
async def get_kinds():
    return kinds.image_kinds


@router.get("/bits", response_model=list[ImageDetail])
async def get_images(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()

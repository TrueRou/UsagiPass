from fastapi import APIRouter, Depends
from sqlmodel import Session, or_, select

from usagipass.app.models import ServerMessage, Image, ImageDetail, User, image_kinds
from usagipass.app.database import require_session
from usagipass.app.usecases import authorize
from usagipass.app.settings import maimai_version, server_motd, author_motd


router = APIRouter(tags=["servers"])


@router.get("/motd")
async def get_motd():
    return ServerMessage(maimai_version=maimai_version, server_motd=server_motd, author_motd=author_motd)


@router.get("/kinds")
async def get_kinds():
    return image_kinds


@router.get("/bits", response_model=list[ImageDetail])
async def get_images(user: User | None = Depends(authorize.verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user.username)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()

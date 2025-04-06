from fastapi import APIRouter, Depends
from sqlmodel import Session, col, or_, select

from usagipass.app.models import ImagePublic, Image, User, image_kinds
from usagipass.app.database import require_session
from usagipass.app.usecases import authorize


router = APIRouter(tags=["servers"])


@router.get("/kinds")
async def get_kinds():
    return image_kinds


@router.get("/bits", response_model=list[ImagePublic])
async def get_images(user: User | None = Depends(authorize.verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(col(Image.uploaded_at).desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user.username)).order_by(col(Image.uploaded_at).desc())
        return session.exec(clause).all()

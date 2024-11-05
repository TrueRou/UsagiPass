from fastapi import APIRouter, Depends
from sqlmodel import Session, or_, select

from app.database import require_session
from app.models.image import Image, ImageDetail
from app.api.users import verify_user_optional

router = APIRouter(prefix="/bits", tags=["bits"])


@router.get("/", response_model=list[ImageDetail])
async def get_images(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()

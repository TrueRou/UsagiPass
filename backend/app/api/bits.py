from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlmodel import Session, or_, select

from app.database import require_session
from app.models.image import Image, ImageDetail
from app.api.users import verify_user_optional
from app.api.images import require_image
from app.maimai import kinds

router = APIRouter(prefix="/bits", tags=["images"])


@router.get("/", response_model=list[ImageDetail])
async def get_images(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()


@router.get("/related/{image_id}", response_model=list[ImageDetail])
async def get_related_images(session: Session = Depends(require_session), image: Image = Depends(require_image)):
    # we don't verify the image here, due to related images are usually from SEGA
    if not image.sega_name:
        return []
    suffix = kinds.remove_sega_prefix(image.sega_name)
    results = session.exec(select(Image).where(Image.sega_name.endswith(suffix)))
    return results.all()

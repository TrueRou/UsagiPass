import io
from pathlib import Path
import uuid
import PIL.Image
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, or_, select

from app.database import require_session
from app.models.image import Image, ImageDetail, ImagePublic
from app.api.users import verify_user, verify_user_optional
from app import database


router = APIRouter(prefix="/images", tags=["images"])
images_folder = Path.cwd() / ".data"
if not images_folder.exists():
    images_folder.mkdir()


@router.get("/gallery", response_model=list[ImageDetail])
async def get_gallery(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()


@router.post("/upload", response_model=ImageDetail, status_code=status.HTTP_201_CREATED)
async def upload_image(
    name: str,
    kind: str,
    user: str = Depends(verify_user),
    file: UploadFile = File(...),
    session: Session = Depends(require_session),
):
    if kind not in ["background", "frame", "character"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid kind of image")
    image_bytes = await file.read()
    try:
        image: PIL.Image = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        image.save(images_folder / f"{db_image.id}.webp", "webp")
        db_image = await database.add(session, Image(name=name, kind=kind, source="external", uploaded_by=user))
        return db_image
    except PIL.UnidentifiedImageError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to load image file")


@router.get("/dl/{image_id}")
async def get_image(image_id: uuid.UUID, session: Session = Depends(require_session)):
    image = session.get(Image, str(image_id))
    try:
        image_path = images_folder / f"{image.id}.png"
        return FileResponse(image_path, media_type="image/png")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file is not found")

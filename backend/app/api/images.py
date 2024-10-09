import io
from pathlib import Path
import uuid
import PIL.Image
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, or_, select

from app.database import require_session
from app.models.image import Image, ImageDetail
from app.api.users import verify_user, verify_user_optional
from app.maimai import kinds
from app import database


router = APIRouter(prefix="/images", tags=["images"])
images_folder = Path.cwd() / ".data" / "images"
if not images_folder.exists():
    images_folder.mkdir()

def get_folder():
    return images_folder

@router.get("/", response_model=list[ImageDetail])
async def get_images(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()


@router.post("/", response_model=ImageDetail, status_code=status.HTTP_201_CREATED)
async def upload_image(
    name: str,
    kind: str,
    user: str = Depends(verify_user),
    file: UploadFile = File(...),
    session: Session = Depends(require_session),
):
    if kind not in kinds.image_kinds.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid kind of image")
    image_bytes = await file.read()
    try:
        file_name = str(uuid.uuid4())
        image: PIL.Image = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        kinds.verify_kind(image, kind)
        image.save(images_folder / f"{file_name}.webp", "webp", optimize=True, quality=80)
        db_image: Image = database.add(session, Image(id=file_name, name=name, kind=kind, uploaded_by=user))
        return db_image
    except PIL.UnidentifiedImageError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to load image file")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Irregular width or height")


@router.delete("/{image_id}")
async def delete_image(image_id: uuid.UUID, user: str = Depends(verify_user), session: Session = Depends(require_session)):
    image = session.get(Image, str(image_id))
    if image.uploaded_by != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this image")
    session.delete(image)
    session.commit()
    image_path = images_folder / f"{image.id}.png"
    image_path.unlink(missing_ok=True)
    return {"message": "Image has been deleted"}


@router.get("/{image_id}")
async def get_image(image_id: uuid.UUID, session: Session = Depends(require_session)):
    image = session.get(Image, str(image_id))
    try:
        image_path = images_folder / f"{image.id}.webp"
        return FileResponse(image_path, media_type="image/webp")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file is not found")

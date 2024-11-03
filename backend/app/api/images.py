import io
from pathlib import Path
import uuid
import PIL.Image
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.database import require_session
from app.models.image import Image, ImageDetail
from app.api.users import verify_user
from app.maimai import kinds
from app import database


router = APIRouter(prefix="/images", tags=["images"])
data_folder = Path.cwd() / ".data"
images_folder = Path.cwd() / ".data" / "images"
thumbnail_folder = Path.cwd() / ".data" / "thumbnails"
data_folder.mkdir(exist_ok=True)
images_folder.mkdir(exist_ok=True)
thumbnail_folder.mkdir(exist_ok=True)


def require_image(image_id: uuid.UUID, session: Session = Depends(require_session)) -> Image:
    image = session.get(Image, str(image_id))
    image_path = images_folder / f"{image_id}.webp"
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image is not found")
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file is not found")
    return image


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
async def delete_image(user: str = Depends(verify_user), session: Session = Depends(require_session), image: Image = Depends(require_image)):
    if image.uploaded_by != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this image")
    session.delete(image)
    session.commit()
    image_path = images_folder / f"{image.id}.png"
    image_path.unlink(missing_ok=True)
    return {"message": "Image has been deleted"}


@router.get("/{image_id}")
async def get_image(image: Image = Depends(require_image)):
    image_path = images_folder / f"{image.id}.webp"
    return FileResponse(image_path, media_type="image/webp")


@router.get("/thumbnail/{image_id}")
async def get_image_thumbnail(image_id: uuid.UUID):
    # we don't verify the image here, due to performance reasons
    thumbnail_path = thumbnail_folder / f"{image_id}.webp"
    image_path = images_folder / f"{image_id}.webp"
    if not thumbnail_path.exists():
        if not image_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file is not found")
        thumbnail = PIL.Image.open(image_path)
        thumbnail.thumbnail((256, 256))
        thumbnail.save(thumbnail_path, "webp", optimize=True, quality=80)
    return FileResponse(thumbnail_path, media_type="image/webp")

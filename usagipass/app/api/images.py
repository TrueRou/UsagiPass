import io
import uuid
from pathlib import Path

import PIL.Image
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from PIL.Image import Image as PILImage
from PIL.Image import Resampling
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app.database import require_session, session_ctx
from usagipass.app.models import Image, ImagePublic, User, image_kinds, sega_prefixs
from usagipass.app.usecases.authorize import verify_user

router = APIRouter(prefix="/images", tags=["images"])
data_folder = Path.cwd() / ".data"
images_folder = Path.cwd() / ".data" / "images"
thumbnail_folder = Path.cwd() / ".data" / "thumbnails"
data_folder.mkdir(exist_ok=True)
images_folder.mkdir(exist_ok=True)
thumbnail_folder.mkdir(exist_ok=True)


async def require_image(image_id: uuid.UUID, session: AsyncSession = Depends(require_session)) -> Image:
    image = await session.get(Image, str(image_id))
    image_path = images_folder / f"{image_id}.webp"
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片未找到")
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片文件未找到")
    return image


def _remove_sega_prefix(name: str) -> str:
    for prefix in sega_prefixs:
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


@router.post("", response_model=ImagePublic, status_code=status.HTTP_201_CREATED)
def upload_image(
    name: str,
    kind: str,
    user: User = Depends(verify_user),
    file: UploadFile = File(...),
):
    if kind not in image_kinds.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片种类无效")
    image_bytes = file.file.read()
    try:
        with session_ctx() as session:
            file_name = str(uuid.uuid4())
            image: PILImage = PIL.Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            image = image.resize(image_kinds[kind]["hw"][0], resample=Resampling.BILINEAR)
            image.save(images_folder / f"{file_name}.webp", "webp", optimize=True, quality=80)
            db_image = Image(id=file_name, name=name, kind=kind, uploaded_by=user.username)
            session.add(db_image)
            session.commit()
            session.refresh(db_image)
        return db_image
    except PIL.UnidentifiedImageError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法加载图片文件")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片宽度或高度不规范")


@router.get("/{image_id}")
async def get_image(image: Image = Depends(require_image)):
    image_path = images_folder / f"{image.id}.webp"
    return FileResponse(image_path, media_type="image/webp")


@router.delete("/{image_id}")
async def delete_image(
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
    image: Image = Depends(require_image),
):
    if image.uploaded_by != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您不是此图片的所有者")
    await session.delete(image)
    image_path = images_folder / f"{image.id}.png"
    image_path.unlink(missing_ok=True)
    await session.commit()
    return {"message": "图片已删除"}


@router.patch("/{image_id}")
async def patch_image(
    name: str,
    user: User = Depends(verify_user),
    session: AsyncSession = Depends(require_session),
    image: Image = Depends(require_image),
):
    if image.uploaded_by != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您不是此图片的所有者")
    image.name = name
    await session.commit()
    return {"message": "图片已重命名"}


@router.get("/{image_id}/related", response_model=list[ImagePublic])
async def get_images_related(session: AsyncSession = Depends(require_session), image: Image = Depends(require_image)):
    if image.sega_name:
        suffix = _remove_sega_prefix(image.sega_name)
        return await session.exec(select(Image).where(col(Image.sega_name).endswith(suffix)))
    return []


@router.get("/{image_id}/thumbnail")
def get_image_thumbnail(image_id: uuid.UUID):
    # we don't verify the image here, due to performance reasons
    thumbnail_path = thumbnail_folder / f"{image_id}.webp"
    image_path = images_folder / f"{image_id}.webp"
    if not thumbnail_path.exists():
        if not image_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片文件未找到")
        thumbnail = PIL.Image.open(image_path)
        thumbnail.thumbnail((256, 256))
        thumbnail.save(thumbnail_path, "webp", optimize=True, quality=80)
    return FileResponse(thumbnail_path, media_type="image/webp")

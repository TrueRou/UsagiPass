import io
import os
from pathlib import Path
import sys
import uuid

import PIL
import httpx
from sqlmodel import Session, and_, select
from PIL import Image as PILImage, ImageChops

sys.path.insert(0, os.path.dirname(os.getcwd()))
os.chdir(os.path.dirname(os.getcwd()))

from app.api.images import images_folder
from app.logging import log, Ansi
from app.database import session_ctx, create_db_and_tables, engine
from app.models.image import Image
from app.maimai import kinds

data_folder = Path.cwd() / ".data"
import_folder = Path.cwd() / ".data" / "import"
data_folder.mkdir(exist_ok=True)
import_folder.mkdir(exist_ok=True)
mask_base = PILImage.open(io.BytesIO(httpx.get("https://s2.loli.net/2024/11/01/gDCfokPySl32srL.png").content))


def post_process(kind: str, img: PILImage.Image) -> PILImage.Image:
    if kind == "mask":
        result = PILImage.new("RGBA", img.size)
        result = PILImage.alpha_composite(result, mask_base.convert("RGBA"))
        result = PILImage.alpha_composite(result, img.convert("RGBA"))
        result = ImageChops.invert(result.convert("RGB"))
        return result
    return img


def import_images(kind: str, session: Session):
    images_path = import_folder / kind
    list_path = import_folder / kind / "list.txt"
    success = 0
    failed = 0
    skipped = 0

    if kind not in kinds.image_kinds.keys():
        log(f"Invalid kind of image: {kind}", Ansi.LRED)
        return

    images_path.mkdir(exist_ok=True)  # create the folder if it doesn't exist
    dictionary = kinds.parse_dictionary(list_path)  # load the dictionary

    for file in images_path.iterdir():
        if file.is_file() and file.suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            try:
                matched_name = dictionary.get(file.stem, file.stem)  # try matching the name from the dictionary
                previous = session.exec(select(Image).where(and_(Image.sega_name == file.stem, Image.kind == kind))).first()
                if not previous:
                    # this is a new image
                    idx = str(uuid.uuid4())
                    img = PILImage.open(file)
                    kinds.verify_kind(img, kind)  # check if the image is of the correct kind
                    img = post_process(kind, img)  # post-process the image for the specific kind to perform effects
                    img.save(images_folder / f"{idx}.webp", "webp", optimize=True, quality=80)
                    session.add(Image(id=idx, name=matched_name, sega_name=file.stem, kind=kind))
                    success += 1
                else:
                    # this image already exists
                    log(f"Image {matched_name} of kind {kind} already exists, skipping", Ansi.LYELLOW)
                    skipped += 1
            except PIL.UnidentifiedImageError:
                failed += 1
            except ValueError:
                failed += 1

    log(f"Imported {success + failed + skipped} images of {kind}, {success} success, {skipped} skipped and {failed} failed", Ansi.LGREEN)


if __name__ == "__main__":
    create_db_and_tables(engine)  # ensure the database is created
    with session_ctx() as session:
        import_images("background", session)
        import_images("frame", session)
        import_images("character", session)
        import_images("passname", session)
        import_images("mask", session)
        session.commit()
    log("Import process complete.", Ansi.LGREEN)

import os
from pathlib import Path
import sys
import uuid

import PIL
from sqlmodel import Session
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.getcwd()))
os.chdir(os.path.dirname(os.getcwd()))

from app.api.images import images_folder
from app.logging import log, Ansi
from app.database import session_ctx, create_db_and_tables, engine
from app.models.image import Image
from app.maimai import kinds

import_folder = Path.cwd() / ".data" / "import"

def import_images(kind: str, session: Session):
    path = import_folder / kind
    success = 0
    failed = 0

    if not path.exists():
        return
    
    if kind not in ["background", "frame", "character"]:
        log(f"Invalid kind of image: {kind}", Ansi.LRED)
        return
    
    for file in path.iterdir():
        if file.is_file():
            try:
                file_name = str(uuid.uuid4())
                img = PILImage.open(file)
                kinds.verify_kind(img, kind)
                img.save(images_folder / f"{file_name}.webp", "webp", optimize=True, quality=80)
                session.add(Image(id=file_name, name=file.stem, kind=kind))
                file.unlink() # delete the file after importing
                success += 1
            except PIL.UnidentifiedImageError:
                failed += 1
            except ValueError:
                failed += 1

    log(f"Imported {success + failed} images of kind {kind}, {success} success and {failed} failed", Ansi.LGREEN)

if __name__ == "__main__":
    create_db_and_tables(engine) # ensure the database is created
    if not import_folder.exists():
        import_folder.mkdir()
    with session_ctx() as session:
        import_images("background", session)
        import_images("frame", session)
        import_images("character", session)
        session.commit()
    log("Import process complete.", Ansi.LGREEN)
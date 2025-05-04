import io
import uuid
import PIL
import httpx
from pathlib import Path
from sqlmodel import Session, and_, select
from PIL import Image as PILImage, ImageChops
from PIL.ImageFile import ImageFile

from usagipass.app.logging import log, Ansi
from usagipass.app.api.images import images_folder
from usagipass.app.database import session_ctx, init_db
from usagipass.app.models import Image, image_kinds

data_folder = Path.cwd() / ".data"
import_folder = Path.cwd() / ".data" / "import"
data_folder.mkdir(exist_ok=True)
import_folder.mkdir(exist_ok=True)
mask_base = PILImage.open(io.BytesIO(httpx.get("https://s2.loli.net/2024/11/01/gDCfokPySl32srL.png").content))


def _verify_kind(img: ImageFile, kind: str):
    if kind not in image_kinds:
        raise ValueError(f"Invalid kind of image.")

    for hw in image_kinds[kind]["hw"]:
        if img.width == hw[0] and img.height == hw[1]:
            return
    raise ValueError(f"Irregular width or height.")


def _parse_dictionary(file: Path):
    result = {}
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                file_str, name = line.split(" ", maxsplit=1)
                file1 = file_str.replace("cardChara0", "UI_CardChara_")
                result[file1] = name
                file2 = file_str.replace("cardChara00", "UI_CardChara_")  # SBGA what are you doing?
                result[file2] = name
    return result


def post_process(kind: str, img: PILImage.Image) -> PILImage.Image:
    if kind == "mask":
        result = PILImage.new("RGBA", img.size)
        result = PILImage.alpha_composite(result, mask_base.convert("RGBA"))
        result = PILImage.alpha_composite(result, img.convert("RGBA"))
        result = ImageChops.invert(result.convert("RGB"))
        result = result.convert("L").convert("RGBA")
        alpha = result.split()[0]
        result.putalpha(alpha)
        return result
    return img


def import_images(kind: str, session: Session):
    images_path = import_folder / kind
    list_path = import_folder / kind / "list.txt"
    success = 0
    failed = 0
    overwritten = 0

    if kind not in image_kinds.keys():
        log(f"Invalid kind of image: {kind}", Ansi.LRED)
        return

    images_path.mkdir(exist_ok=True)  # create the folder if it doesn't exist
    dictionary = _parse_dictionary(list_path)  # load the dictionary

    for file in images_path.iterdir():
        if file.is_file() and file.suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            try:
                matched_name = dictionary.get(file.stem, file.stem)  # try matching the name from the dictionary
                previous = session.exec(select(Image).where(and_(Image.sega_name == file.stem, Image.kind == kind))).first()
                # check if the image already exists (overwrite if exists)
                if previous:
                    old_file = images_folder / f"{previous.id}.webp"
                    session.delete(previous)  # delete the previous entry
                    old_file.unlink()  # delete the old file
                    log(f"Image {matched_name} of kind {kind} already exists, overwriting", Ansi.LYELLOW)
                    overwritten += 1
                idx = str(uuid.uuid4())
                img = PILImage.open(file)
                _verify_kind(img, kind)  # check if the image is of the correct kind
                img = post_process(kind, img)  # post-process the image for the specific kind to perform effects
                img.save(images_folder / f"{idx}.webp", "webp", optimize=True, quality=80)
                session.add(Image(id=idx, name=matched_name, sega_name=file.stem, kind=kind))
                file.unlink()  # delete the success file after importing
                success += 1
            except PIL.UnidentifiedImageError:
                failed += 1
            except ValueError:
                failed += 1

    log(f"Imported {success + failed} images of {kind}, {success} success ({overwritten} overwritten) and {failed} failed", Ansi.LGREEN)


def main():
    init_db(skip_migration=True)  # ensure the database is created
    with session_ctx() as session:
        import_images("background", session)
        import_images("frame", session)
        import_images("character", session)
        import_images("passname", session)
        import_images("mask", session)
        session.commit()
    log("Import process complete.", Ansi.LGREEN)


if __name__ == "__main__":
    main()

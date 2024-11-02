from pathlib import Path
from PIL import ImageFile

image_kinds = {
    "background": {"hw": [(768, 1052)]},
    "frame": {"hw": [(768, 1052)]},
    "character": {"hw": [(768, 1052), (1024, 1408)]},
    "mask": {"hw": [(768, 1052), (1024, 1408)]},
    "passname": {"hw": [(338, 112), (363, 110), (374, 105), (415, 115)]},
}

sega_prefixs = ["UI_CardChara_", "UI_CardBase_", "UI_CMA_", "UI_CardCharaMask_"]


def verify_kind(img: ImageFile, kind: str):
    if kind not in image_kinds:
        raise ValueError(f"Invalid kind of image.")

    for hw in image_kinds[kind]["hw"]:
        if img.width == hw[0] and img.height == hw[1]:
            return
    raise ValueError(f"Irregular width or height.")


def parse_dictionary(file: Path):
    result = {}
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                file, name = line.split(" ", maxsplit=1)
                file1 = file.replace("cardChara0", "UI_CardChara_")
                result[file1] = name
                file2 = file.replace("cardChara00", "UI_CardChara_")  # SBGA what are you doing?
                result[file2] = name
    return result


def remove_sega_prefix(name: str) -> str:
    for prefix in sega_prefixs:
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name

from PIL import ImageFile

image_kinds = {
    "background": {
        "hw": [(768, 1052)]
    },
    "frame": {
        "hw": [(768, 1052)]
    },
    "character": {
        "hw": [(768, 1052), (1024, 1408)]
    },
    "passname": {
        "hw": [(338, 112), (363, 110), (374, 105), (415, 115)]
    }
}

def verify_kind(img: ImageFile, kind: str):
    if kind not in image_kinds:
        raise ValueError(f"Invalid kind of image.")
    
    for hw in image_kinds[kind]["hw"]:
        if img.width == hw[0] and img.height == hw[1]:
            return
    raise ValueError(f"Irregular width or height.")
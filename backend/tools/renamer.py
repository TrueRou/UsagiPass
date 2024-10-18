import os
from pathlib import Path
import re
import sys

sys.path.insert(0, os.path.dirname(os.getcwd()))
os.chdir(os.path.dirname(os.getcwd()))

from app.logging import log, Ansi

data_folder = Path.cwd() / ".data"
maimai_folder = Path.cwd() / ".data" / "maimai" / "character"
import_folder = Path.cwd() / ".data" / "import" / "character"
data_folder.mkdir(exist_ok=True)
maimai_folder.mkdir(exist_ok=True)
import_folder.mkdir(exist_ok=True)


def find_name(file: Path):
    pattern = r'[<>:"/\\|?*]'
    vaild_name = re.sub(pattern, "_", file.stem)
    file = file.with_stem(vaild_name)
    if file.is_file():
        file = file.with_stem(file.stem + "#")
    return file if not file.is_file() else find_name(file)


if not (maimai_folder / "list.txt").exists():
    log(f"Character list not exists in {maimai_folder / "list.txt"}", Ansi.LRED)
else:
    with open(maimai_folder / "list.txt", "r", encoding="utf-8") as f:
        chara_dict = {}
        for line in f.read().splitlines():
            file, name = line.split(" ", maxsplit=1)
            file1 = file.replace("cardChara0", "UI_CardChara_")
            chara_dict[file1] = name
            file2 = file.replace("cardChara00", "UI_CardChara_")  # SBGA what are you doing?
            chara_dict[file2] = name

        for file in maimai_folder.iterdir():
            if file.is_file() and file.stem in chara_dict.keys():
                new_file = find_name(import_folder / f"{chara_dict[file.stem]}.png")
                file.rename(new_file)
                log(f"Renamed {file.name} to {chara_dict[file.stem]}", Ansi.LGREEN)

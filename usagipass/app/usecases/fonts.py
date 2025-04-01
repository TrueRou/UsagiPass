from fastapi import HTTPException, status
from fontTools.ttLib import TTFont

from usagipass.app.models import PreferencePublic

font = TTFont("usagipass/app/usecases/static/SEGAMaruGothicDB.woff2")
uniMap = font["cmap"].tables[0].ttFont.getBestCmap()


def str_in_font(string: str) -> tuple[bool, list[str]]:
    missing_chars = []
    for char in string:
        if ord(char) not in uniMap:
            missing_chars.append(char)
    return len(missing_chars) == 0, missing_chars


def preference_in_font(preference: PreferencePublic) -> tuple[bool, list[str]]:
    fields = ["display_name", "friend_code", "maimai_version", "simplified_code", "character_name"]
    preference_str = "".join([getattr(preference, field) or "" for field in fields])
    return str_in_font(preference_str)


def check_preference_throw(preference: PreferencePublic) -> None:
    legal, lacks = preference_in_font(preference)
    if not legal:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"字体中缺少以下字符: {', '.join(lacks)}")

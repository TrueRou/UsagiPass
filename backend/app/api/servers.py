from fastapi import APIRouter

from app.models.server import ServerMessage
from app.maimai import kinds
import config


router = APIRouter(tags=["servers"])


@router.get("/motd")
async def get_motd():
    return ServerMessage(
        maimai_version=config.maimai_version,
        server_motd=config.server_motd,
        author_motd=config.author_motd,
    )


@router.get("/kinds")
async def get_kinds():
    return kinds.image_kinds

from fastapi import APIRouter

from app.models.server import ServerMessage
import config


router = APIRouter(prefix="/", tags=["servers"])


@router.get("/motd")
async def get_motd():
    return ServerMessage(
        maimai_version=config.maimai_version,
        server_motd=config.server_motd,
        author_motd=config.author_motd,
    )

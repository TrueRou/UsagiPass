from __future__ import annotations
import asyncio

from fastapi import FastAPI
from httpx import ConnectError, ReadTimeout
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

from app import database
from app import api
from app.database import async_session_ctx
from app.logging import log, Ansi
from app.maimai import music, scores


def init_middlewares(asgi_app: FastAPI) -> None:
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    asgi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    database.register_middleware(asgi_app)


def init_events(asgi_app: FastAPI) -> None:
    async def download_music_list() -> None:
        await asyncio.sleep(1)  # Wait for web server to start
        log("Started downloading maimai music list.", Ansi.LYELLOW)
        try:
            scores.music_list = await music.download_music_list()
            log("Finished downloading maimai music list.", Ansi.LGREEN)
        except (ConnectError, ReadTimeout):
            log("Failed to download maimai music list.", Ansi.LRED)

    @asgi_app.on_event("startup")
    async def on_startup() -> None:
        async with async_session_ctx() as session:
            await session.execute(text("SELECT 1"))  # Test connection
            database.create_db_and_tables(database.engine)  # TODO: Sql migration
            asyncio.ensure_future(download_music_list())  # Download music list from diving-fish
            log("Startup process complete.", Ansi.LGREEN)

    @asgi_app.on_event("shutdown")
    async def on_shutdown() -> None:
        await database.async_engine.dispose()
        database.engine.dispose()


def init_routes(asgi_app: FastAPI) -> None:
    asgi_app.include_router(api.router)


def init_api() -> FastAPI:
    """Create & initialize our app."""
    asgi_app = FastAPI()

    init_middlewares(asgi_app)
    init_events(asgi_app)
    init_routes(asgi_app)

    return asgi_app


asgi_app = init_api()

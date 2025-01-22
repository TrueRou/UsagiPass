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
from app.maimai import crawler


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


async def init_lifespan(asgi_app: FastAPI):
    async def download_music_list() -> None:
        try:
            await crawler.maimai.songs(alias_provider=None, curve_provider=None)
            log("Finished downloading maimai music list.", Ansi.LGREEN)
        except (ConnectError, ReadTimeout):
            log("Failed to download maimai music list.", Ansi.LRED)

    async def connect_to_database() -> None:
        try:
            async with async_session_ctx() as session:
                await session.execute(text("SELECT 1"))
                database.create_db_and_tables(database.engine)
            log("Finished connecting to the database.", Ansi.LGREEN)
        except (ConnectError, ReadTimeout):
            log("Failed to connect to the database.", Ansi.LRED)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(connect_to_database())
        tg.create_task(download_music_list())
    yield
    async with asyncio.TaskGroup() as tg:
        tg.create_task(database.async_engine.dispose())
        database.engine.dispose()


def init_routes(asgi_app: FastAPI) -> None:
    asgi_app.include_router(api.router)


def init_api() -> FastAPI:
    """Create & initialize our app."""
    asgi_app = FastAPI(lifespan=init_lifespan)

    init_middlewares(asgi_app)
    init_routes(asgi_app)

    return asgi_app


asgi_app = init_api()

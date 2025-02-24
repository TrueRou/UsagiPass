from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from usagipass.app import database
from usagipass.app.logging import log, Ansi
from usagipass.app.usecases import crawler


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


@asynccontextmanager
async def init_lifespan(asgi_app: FastAPI):
    database.init_db()
    await crawler.maimai.songs(alias_provider=None, curve_provider=None)
    log("Startup process complete.", Ansi.LGREEN)
    yield  # Above: Startup process Below: Shutdown process
    await database.async_engine.dispose()
    database.engine.dispose()


def init_routes(asgi_app: FastAPI) -> None:
    from usagipass.app import api

    @asgi_app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Welcome to UsagiPass backend!"}

    asgi_app.include_router(api.router)


def init_api() -> FastAPI:
    """Create & initialize our app."""
    asgi_app = FastAPI(lifespan=init_lifespan)

    init_middlewares(asgi_app)
    init_routes(asgi_app)

    return asgi_app


asgi_app = init_api()

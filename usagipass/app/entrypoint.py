from __future__ import annotations

import asyncio
import logging
from fastapi import FastAPI
from mitmproxy.master import Master
from mitmproxy.options import Options
from mitmproxy.addons import default_addons
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from usagipass.app import database, settings
from usagipass.app.logging import log, Ansi
from usagipass.app.usecases import scheduler
from usagipass.app.usecases.addons import WechatWahlapAddon


class MitmMaster(Master):
    def __init__(self):
        super().__init__(Options())
        self.addons.add(*default_addons())
        self.addons.add(WechatWahlapAddon())
        self.options.update(
            listen_host=settings.mitm_host,
            listen_port=settings.mitm_port,
            block_global=False,
            connection_strategy="lazy",
        )

    async def run(self):
        log(f"Mitmproxy running on http://{settings.mitm_host}:{str(settings.mitm_port)} (Press CTRL+C to quit)", Ansi.LCYAN)
        return await super().run()

    def _asyncio_exception_handler(self, loop, context):
        exc: Exception = context["exception"]
        logging.exception(exc)
        return super()._asyncio_exception_handler(loop, context)


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
    asyncio.create_task(MitmMaster().run())
    asyncio.create_task(scheduler.init_sched())
    log("Startup process complete.", Ansi.LGREEN)
    yield  # Above: Startup process Below: Shutdown process
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

import contextlib
from fastapi import Request
import httpx
from sqlalchemy import text
from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import config


engine = create_engine(config.database_url)
async_engine = create_async_engine(config.database_url.replace("sqlite://", "sqlite+aiosqlite://"))


async def create_db_and_tables(engine):
    import app.models  # make sure all models are imported (keep its record in metadata)

    app.models.SQLModel.metadata.create_all(engine)


# https://stackoverflow.com/questions/75487025/how-to-avoid-creating-multiple-sessions-when-using-fastapi-dependencies-with-sec
def register_middleware(asgi_app):
    @asgi_app.middleware("http")
    async def session_middleware(request: Request, call_next):
        with Session(engine, expire_on_commit=False) as session:
            request.state.session = session
            response = await call_next(request)
            return response


def require_session(request: Request):
    return request.state.session


@contextlib.contextmanager
def session_ctx():
    with Session(engine, expire_on_commit=False) as session:
        yield session


@contextlib.asynccontextmanager
async def async_session_ctx():
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


@contextlib.asynccontextmanager
async def async_httpx_ctx():
    async with httpx.AsyncClient(proxies=config.httpx_proxy) as session:
        yield session

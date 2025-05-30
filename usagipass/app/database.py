import asyncio
import contextlib
from typing import AsyncGenerator, Generator, TypeVar
from urllib.parse import unquote, urlparse

import httpx
from aiocache import RedisCache
from aiocache.serializers import PickleSerializer
from fastapi import Request
from maimai_py import MaimaiClient
from maimai_py.utils.sentinel import UNSET
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool, QueuePool
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from usagipass.app import settings
from usagipass.app.logging import Ansi, log

engine = create_engine(settings.mysql_url, poolclass=QueuePool)
async_engine = create_async_engine(settings.mysql_url.replace("mysql+pymysql", "mysql+aiomysql"), poolclass=AsyncAdaptedQueuePool)
redis_backend = UNSET
if settings.redis_url:
    redis_url = urlparse(settings.redis_url)
    redis_backend = RedisCache(
        serializer=PickleSerializer(),
        endpoint=unquote(redis_url.hostname or "localhost"),
        port=redis_url.port or 6379,
        password=redis_url.password,
        db=int(unquote(redis_url.path).replace("/", "")),
    )
maimai_client = MaimaiClient(cache=redis_backend)
httpx_client = httpx.AsyncClient(proxy=settings.httpx_proxy, timeout=20)

V = TypeVar("V")


@contextlib.asynccontextmanager
async def async_session_ctx() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


@contextlib.contextmanager
def session_ctx() -> Generator[Session, None, None]:
    with Session(engine, expire_on_commit=False) as session:
        yield session


def init_db(skip_migration: bool = False) -> None:
    from sqlalchemy import text
    import alembic.command as command
    from alembic.config import Config as AlembicConfig

    try:
        with session_ctx() as session:
            session.execute(text("SELECT 1"))
    except OperationalError:
        log("Failed to connect to the database.", Ansi.LRED)
    if not skip_migration:
        try:
            with engine.connect() as connection:
                result1 = connection.execute(text("SHOW TABLES LIKE 'alembic_version'"))
                result2 = connection.execute(text("SHOW TABLES LIKE 'users'"))
                if not result1.fetchone() and result2.fetchone():
                    # If alembic_version table does not exist but users table does, then the database is outdated
                    log("You are running an outdated database schema. Running migration...", Ansi.YELLOW)
                    command.stamp(AlembicConfig(config_args={"script_location": "alembic"}), "9cdcf6f8ca8c")
            command.upgrade(AlembicConfig(config_args={"script_location": "alembic"}), "head")
        except Exception as e:
            log(f"Failed to run database migration: {e}", Ansi.LRED)


# https://stackoverflow.com/questions/75487025/how-to-avoid-creating-multiple-sessions-when-using-fastapi-dependencies-with-sec
def register_middleware(asgi_app):
    @asgi_app.middleware("http")
    async def session_middleware(request: Request, call_next):
        async with async_session_ctx() as session:
            request.state.session = session
            response = await call_next(request)
            return response


def require_session(request: Request):
    return request.state.session


async def add_model(session: AsyncSession, *models):
    [session.add(model) for model in models if model]
    await session.flush()
    await asyncio.gather(*[session.refresh(model) for model in models if model])


async def partial_update_model(session: AsyncSession, item: SQLModel, updates: SQLModel):
    if item and updates:
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await session.flush()
        await session.refresh(item)

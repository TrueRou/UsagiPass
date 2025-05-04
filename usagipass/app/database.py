import contextlib
import httpx
from typing import Generator, TypeVar
from fastapi import Request
from maimai_py import MaimaiClient
from sqlalchemy import text
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, create_engine, Session

from usagipass.app import settings
from usagipass.app.logging import log, Ansi


engine = create_engine(settings.mysql_url)
maimai_client = MaimaiClient()

V = TypeVar("V")


def init_db(skip_migration: bool = False) -> None:
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
        with Session(engine, expire_on_commit=False) as session:
            request.state.session = session
            response = await call_next(request)
            return response


def require_session(request: Request):
    return request.state.session


@contextlib.contextmanager
def session_ctx() -> Generator[Session, None, None]:
    with Session(engine, expire_on_commit=False) as session:
        yield session


@contextlib.asynccontextmanager
async def async_httpx_ctx():
    async with httpx.AsyncClient(proxy=settings.httpx_proxy, timeout=20) as session:
        yield session


def add_model(session: Session, *models):
    [session.add(model) for model in models if model]
    session.commit()
    [session.refresh(model) for model in models if model]


def partial_update_model(session: Session, item: SQLModel, updates: SQLModel):
    if item and updates:
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        session.commit()
        session.refresh(item)

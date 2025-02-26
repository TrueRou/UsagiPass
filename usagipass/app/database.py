import contextlib
import httpx
from typing import TypeVar
from fastapi import Request
from sqlalchemy import text
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, create_engine, Session

from usagipass.app import settings
from usagipass.app.logging import log, Ansi


engine = create_engine(settings.mysql_url)

V = TypeVar("V")


def init_db():
    try:
        with session_ctx() as session:
            session.exec(text("SELECT 1"))
    except OperationalError:
        log("Failed to connect to the database.", Ansi.RED)
    try:
        command.upgrade(AlembicConfig(config_args={"script_location": "alembic"}), "head")
    except Exception as e:
        log(f"Failed to run database migration: {e}", Ansi.RED)


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

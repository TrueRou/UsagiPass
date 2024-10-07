from typing import TypeVar
from fastapi import APIRouter, Depends
from sqlmodel import Session, or_, select

from app.database import require_session
from app.models.element import Background, Character, Frame
from app.api.users import verify_user_optional


router = APIRouter(prefix="/elements", tags=["elements"])

T = TypeVar("T", Background, Character, Frame)


def fetch_conditional(user: str | None, model: T, session: Session) -> list[T]:
    clause = select(model).order_by(model.uploaded_at.desc())
    if user is None:
        clause = clause.where(model.uploaded_by == None)
    else:
        clause = clause.where(or_(model.uploaded_by == None, model.uploaded_by == user))
    return session.exec(clause).all()


@router.get("/backgrounds")
async def get_backgrounds(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    return fetch_conditional(user, Background, session)


@router.get("/frames")
async def get_frames(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    return fetch_conditional(user, Frame, session)


@router.get("/characters")
async def get_characters(user: str | None = Depends(verify_user_optional), session: Session = Depends(require_session)):
    return fetch_conditional(user, Character, session)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, or_, select

from usagipass.app.models import PreferencePublic, ServerMessage, Image, ImageDetail, User, image_kinds
from usagipass.app.database import require_session
from usagipass.app.usecases import authorize
from usagipass.app.settings import maimai_version, server_motd, author_motd
from usagipass.app.settings import default_background, default_character, default_frame, default_passname


router = APIRouter(tags=["servers"])


@router.get("/motd")
async def get_motd():
    return ServerMessage(maimai_version=maimai_version, server_motd=server_motd, author_motd=author_motd)


@router.get("/kinds")
async def get_kinds():
    return image_kinds


@router.get("/bits", response_model=list[ImageDetail])
async def get_images(user: User | None = Depends(authorize.verify_user_optional), session: Session = Depends(require_session)):
    if user is None:
        clause = select(Image).where(Image.uploaded_by == None).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()
    else:
        clause = select(Image).where(or_(Image.uploaded_by == None, Image.uploaded_by == user.username)).order_by(Image.uploaded_at.desc())
        return session.exec(clause).all()


@router.get("/defaults", response_model=PreferencePublic)
async def get_defaults(session: Session = Depends(require_session)):
    # we need to get the image objects from the database
    character = session.get(Image, default_character)
    background = session.get(Image, default_background)
    frame = session.get(Image, default_frame)
    passname = session.get(Image, default_passname)
    if None in [character, background, frame, passname]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default image not found in database, please contact the administrator"
        )
    return PreferencePublic(
        character=ImageDetail.model_validate(character),
        background=ImageDetail.model_validate(background),
        frame=ImageDetail.model_validate(frame),
        passname=ImageDetail.model_validate(passname),
    )

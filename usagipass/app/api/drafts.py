import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from usagipass.app import database
from usagipass.app.api.cards import require_card, require_preference
from usagipass.app.database import partial_update_model, require_session
from usagipass.app.models import Card, CardPreference, CardStatus, PreferencePublic, PreferenceUpdate


router = APIRouter(prefix="/drafts", tags=["drafts"])


def require_phone(phone: str) -> str:
    if not phone.isdigit() or len(phone) != 11:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")
    return phone


def require_draft(card: Card = Depends(require_card)) -> Card:
    if card.status == CardStatus.DRAFTED:
        return card
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card is not a draft")


@router.get("", response_model=list[Card])
async def get_drafts(phone: str = Depends(require_phone), session: Session = Depends(require_session)):
    clause = select(Card).where(Card.phone == phone, Card.status != CardStatus.ACTIVATED).order_by(Card.created_at.desc())
    return session.exec(clause).all()


@router.post("", response_model=Card)
async def create_draft(phone: str = Depends(require_phone), session: Session = Depends(require_session)):
    new_uuid = str(uuid.uuid4())
    card = Card(uuid=new_uuid, phone=phone)
    preference = CardPreference(uuid=new_uuid)
    database.add_model(session, card, preference)
    return card


@router.delete("/{uuid}")
async def delete_draft(draft: Card = Depends(require_draft), session: Session = Depends(require_session)):
    session.delete(draft)
    session.commit()
    return {"message": "Draft has been deleted"}


@router.patch("/{uuid}/preference", dependencies=[Depends(require_draft)])
async def update_preference(
    updates: PreferencePublic,
    preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
):
    update_preference = PreferenceUpdate(
        **updates.model_dump(exclude={"character", "background", "frame", "passname", "simplified_code"}),
        character_id=updates.character.id if updates.character else None,
        background_id=updates.background.id if updates.background else None,
        frame_id=updates.frame.id if updates.frame else None,
        passname_id=updates.passname.id if updates.passname else None,
    )
    # there's no problem with the image ids, we can update the preference
    partial_update_model(session, preference, update_preference)
    return {"message": "Preference has been updated"}

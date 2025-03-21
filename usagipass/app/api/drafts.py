import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from usagipass.app import database
from usagipass.app.api.cards import require_card, require_preference
from usagipass.app.database import partial_update_model, require_session
from usagipass.app.models import Card, CardPreference, PreferencePublic, PreferenceUpdate


router = APIRouter(prefix="/drafts", tags=["drafts"])


def require_phone(phone: str) -> str:
    if not phone.isdigit() or len(phone) != 11:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number")
    return phone


def require_draft(card: Card = Depends(require_card)) -> Card:
    if card.card_id is None:
        return card
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card was out of draft state")


@router.get("", response_model=list[Card])
async def get_drafts(phone: str = Depends(require_phone), session: Session = Depends(require_session)):
    return session.exec(select(Card).where(Card.phone_number == phone)).all()


@router.post("", response_model=Card)
async def create_draft(phone: str = Depends(require_phone), session: Session = Depends(require_session)):
    card = Card(uuid=str(uuid.uuid4()), phone_number=phone)
    database.add_model(session, card)
    preference = CardPreference(uuid=card.uuid)
    database.add_model(session, preference)
    return card


@router.delete("/{uuid}")
async def delete_draft(draft: Card = Depends(require_draft), session: Session = Depends(require_session)):
    session.delete(draft)
    session.commit()
    return {"message": "Draft has been deleted"}


@router.patch("/{uuid}/preference")
async def update_preference(
    preference: PreferencePublic,
    draft: Card = Depends(require_draft),
    db_preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
):
    update_preference = PreferenceUpdate(
        **preference.model_dump(exclude={"character", "background", "frame", "passname"}),
        character_id=preference.character.id if preference.character else None,
        background_id=preference.background.id if preference.background else None,
        frame_id=preference.frame.id if preference.frame else None,
        passname_id=preference.passname.id if preference.passname else None,
    )
    # there's no problem with the image ids, we can update the preference
    partial_update_model(session, db_preference, update_preference)
    return {"message": "Preference has been updated"}

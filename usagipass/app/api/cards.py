import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from usagipass.app.database import require_session
from usagipass.app.models import Card, CardPreference, CardProfile, CardUser, PreferencePublic
from usagipass.app.usecases import maimai
from usagipass.app.usecases.accounts import apply_preference


router = APIRouter(prefix="/users", tags=["users"])


def require_card(uuid: str, session: Session = Depends(require_session)) -> Card:
    card = session.exec(select(Card).where(Card.uuid == uuid)).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


@router.get("/profile", response_model=CardProfile)
async def get_profile(card: Card = Depends(require_card), session: Session = Depends(require_session)):
    db_account = session.exec(select(CardUser).where(CardUser.id == card.user_id)).first()
    db_preference = session.get(CardPreference, card.cid)
    # we need to trigger the scores updating if the user has not updated for a while
    asyncio.create_task(maimai.update_scores_passive(card))
    preferences = PreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    card_profile = CardProfile(
        cid=card.cid,
        player_rating=db_account.mai_rating,
        preferences=preferences,
    )
    return card_profile

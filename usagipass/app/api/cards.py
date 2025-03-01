import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from maimai_py.exceptions import AimeServerError

from usagipass.app import settings
from usagipass.app.logging import log, Ansi
from usagipass.app.database import require_session, maimai_client
from usagipass.app.models import Card, CardPreference, CardProfile, CardUser, PreferencePublic
from usagipass.app.usecases import maimai
from usagipass.app.usecases.accounts import apply_preference


router = APIRouter(prefix="/cards", tags=["cards"])


def require_card(uuid: str, session: Session = Depends(require_session)) -> Card:
    card = session.exec(select(Card).where(Card.uuid == uuid)).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


@router.post("/activate")
async def activate_card(qrcode: str, card: Card = Depends(require_card), session: Session = Depends(require_session)):
    if card.user_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card has already been activated")
    try:
        credentials = await maimai_client.qrcode(qrcode, settings.arcade_proxy)
        card_user = CardUser(mai_userid=credentials.credentials, mai_rating=0)
        session.add(card_user)
        session.flush()
        card.user_id = card_user.id
        session.commit()
    except AimeServerError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid QR code or expired")
    except Exception as e:
        log(f"Failed to activate card of {card.cid}: {repr(e)}", Ansi.LRED)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate card")
    await maimai.update_scores(card_user)
    return {"message": "Card has been activated"}


@router.get("/profile", response_model=CardProfile)
async def get_profile(card: Card = Depends(require_card), session: Session = Depends(require_session)):
    db_account = session.exec(select(CardUser).where(CardUser.id == card.user_id)).first()
    db_preference = session.get(CardPreference, card.cid)
    if not db_account or not db_preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card has not been activated")
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

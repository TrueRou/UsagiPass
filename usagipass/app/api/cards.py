import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status, Body
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from maimai_py import MaimaiScores, MaimaiSongs, Score as MpyScore
from maimai_py.exceptions import AimeServerError

from usagipass.app import settings
from usagipass.app import database
from usagipass.app.logging import log, Ansi
from usagipass.app.database import partial_update_model, require_session, maimai_client
from usagipass.app.models import (
    Card,
    BestsPublic,
    CardPreference,
    CardProfile,
    CardAccount,
    CardAccountPublic,
    CardStatus,
    CardUpdate,
    PreferencePublic,
    PreferenceUpdate,
    Score,
    ScorePublic,
)
from usagipass.app.usecases import maimai
from usagipass.app.usecases.authorize import verify_admin
from usagipass.app.usecases.accounts import apply_preference
from usagipass.app.usecases import browser


router = APIRouter(prefix="/cards", tags=["cards"])


def require_card(uuid: str = Path(...), session: Session = Depends(require_session)) -> Card:
    if card := session.exec(select(Card).where(Card.uuid == uuid)).first():
        return card
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")


def require_card_scheduled(card: Card = Depends(require_card)) -> Card:
    if card.status >= CardStatus.SCHEDULED:
        return card
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card has not been scheduled")


def require_preference(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardPreference:
    if preference := session.get(CardPreference, card.uuid):
        return preference
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card has not been initialized")


def require_card_account(card: Card = Depends(require_card_scheduled), session: Session = Depends(require_session)) -> CardAccount | None:
    if card.account_id and (user := session.get(CardAccount, card.account_id)):
        return user


@router.post("", response_model=Card, dependencies=[Depends(verify_admin)])
async def create_card(session: Session = Depends(require_session)):
    # admin can create a card without a phone number, and skip the draft state
    new_uuid = str(uuid.uuid4())
    card = Card(uuid=new_uuid, status=CardStatus.SCHEDULED)
    preference = CardPreference(uuid=new_uuid)
    database.add_model(session, card, preference)
    return card


@router.get("", response_model=list[Card], dependencies=[Depends(verify_admin)])
async def get_cards(session: Session = Depends(require_session)):
    clause = select(Card).order_by(Card.created_at.desc())
    return session.exec(clause).all()


@router.patch("/{uuid}", dependencies=[Depends(verify_admin)])
async def update_card(
    updates: CardUpdate,
    card: Card = Depends(require_card),
    session: Session = Depends(require_session),
):
    card.updated_at = datetime.utcnow()
    partial_update_model(session, card, updates)
    return {"message": "Card has been updated"}


@router.get("/{uuid}/preference", response_model=PreferencePublic)
async def get_preference(
    db_preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
):
    preferences = PreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    return preferences


@router.patch("/{uuid}/preference", dependencies=[Depends(verify_admin)])
async def update_preference(
    updates: PreferencePublic,
    preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
):
    update_preference = PreferenceUpdate(
        **updates.model_dump(exclude={"character", "background", "frame", "passname"}),
        character_id=updates.character.id if updates.character else None,
        background_id=updates.background.id if updates.background else None,
        frame_id=updates.frame.id if updates.frame else None,
        passname_id=updates.passname.id if updates.passname else None,
    )

    partial_update_model(session, preference, update_preference)
    return {"message": "Preference has been updated"}


@router.post("/{uuid}/accounts")
async def create_account(
    qrcode: str | None = None,
    card: Card = Depends(require_card_scheduled),
    session: Session = Depends(require_session),
):
    if card.status == CardStatus.ACTIVATED and card.account_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card has already been bound to an account")

    if card.status >= CardStatus.SCHEDULED and card.account_id is None and qrcode is None:
        # user skip the activation process, and the card will not bind to any account
        card.status = CardStatus.ACTIVATED
        session.commit()
        return {"message": "Card has been activated with null account"}

    try:
        if card.status >= CardStatus.SCHEDULED:
            credentials = await maimai_client.qrcode(qrcode or "", settings.arcade_proxy)
            account = CardAccount(credentials=credentials.credentials, player_rating=0)
            session.add(account)
            session.flush()
            card.account_id = account.id
            card.status = CardStatus.ACTIVATED
            session.commit()
    except AimeServerError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid QR code or expired")
    except Exception as e:
        log(f"Failed to activate card of {card.id}: {repr(e)}", Ansi.LRED)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate card")
    await maimai.update_scores(account)  # away from try-except block
    return {"message": "Card account has been created"}


@router.patch("/{uuid}/accounts")
async def update_accounts(
    db_account: CardAccount = Depends(require_card_account),
):
    if db_account:
        await maimai.update_scores(db_account)
    return {"message": "Card account has been updated"}


@router.get("/{uuid}/profile", response_model=CardProfile)
async def get_profile(
    card: Card = Depends(require_card_scheduled),
    db_preference: CardPreference = Depends(require_preference),
    account: CardAccount = Depends(require_card_account),
    session: Session = Depends(require_session),
):
    def _ser_scores(mpy_scores: list[MpyScore], songs: MaimaiSongs) -> list[ScorePublic]:
        return [
            ScorePublic(
                **(Score.from_mpy(score, account.id).model_dump()),
                song_name=song.title,
                level=song.get_difficulty(score.type, score.level_index).level,
            )
            for score in mpy_scores
            if (song := songs.by_id(score.id))
        ]

    # prepare the preference
    preferences = PreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    # prepare the accounts
    accounts, bests = None, BestsPublic(b35_scores=[], b15_scores=[], b35_rating=0, b15_rating=0, all_rating=0)
    if account:
        songs = await maimai_client.songs()
        scores = session.exec(select(Score).where(Score.account_id == account.id)).all()
        if len(scores) > 0:
            mscores = MaimaiScores(all=[await Score.as_mpy(score) for score in scores], songs=songs)
            bests = BestsPublic(
                b35_scores=_ser_scores(mscores.scores_b35, songs),
                b15_scores=_ser_scores(mscores.scores_b15, songs),
                b35_rating=mscores.rating_b35,
                b15_rating=mscores.rating_b15,
                all_rating=mscores.rating,
            )
        accounts = CardAccountPublic(player_rating=account.player_rating, created_at=account.created_at, player_bests=bests)

    return CardProfile(
        id=card.id,
        uuid=card.uuid,
        status=card.status,
        preferences=preferences,
        accounts=accounts,
    )


@router.post("/batch/screenshots", dependencies=[Depends(verify_admin)])
async def get_batch_screenshots(
    uuids: List[str] = Body(...),
    session: Session = Depends(require_session),
):
    cards = session.exec(select(Card).where(Card.uuid.in_(uuids), Card.status == CardStatus.SCHEDULED)).all()
    if len(cards) != len(uuids):
        lost_uuids = set(uuids) - {card.uuid for card in cards}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cards are not found: {', '.join(lost_uuids)}")

    _, zip_file = await browser.capture_multiple_screenshot(list(cards))
    return FileResponse(zip_file, media_type="application/zip", filename=f"cards.zip")

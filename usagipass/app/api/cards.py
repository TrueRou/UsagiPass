import uuid
from typing import Literal, List
from fastapi import APIRouter, Depends, HTTPException, Path, status, Body
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from maimai_py import MaimaiScores, MaimaiSongs, Score as MpyScore
from maimai_py.exceptions import AimeServerError
import tempfile
import os
import zipfile
import shutil

from usagipass.app import settings
from usagipass.app import database
from usagipass.app.logging import log, Ansi
from usagipass.app.database import partial_update_model, require_session, maimai_client
from usagipass.app.models import (
    Card,
    BestsPublic,
    CardPreference,
    CardPreferencePublic,
    CardPreferenceUpdate,
    CardPublic,
    CardUser,
    CardUserPublic,
    Privilege,
    Score,
    ScorePublic,
    User,
)
from usagipass.app.usecases import maimai
from usagipass.app.usecases.authorize import verify_admin, verify_user_optional
from usagipass.app.usecases.accounts import apply_preference
from usagipass.app.usecases import browser


router = APIRouter(prefix="/cards", tags=["cards"])


def require_card(uuid: str = Path(...), session: Session = Depends(require_session)) -> Card:
    if card := session.get(Card, uuid):
        return card
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")


def require_card_strict(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> Card:
    if card.card_id is not None:
        return card
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card was in draft state")


def require_preference(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardPreference:
    if preference := session.get(CardPreference, card.uuid):
        return preference
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card has not been initialized")


def require_card_user(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardUser:
    if card.user_id and (user := session.get(CardUser, card.user_id)):
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card has not been activated")


def require_card_user_optional(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardUser | None:
    if card.user_id and (user := session.get(CardUser, card.user_id)):
        return user


@router.post("", response_model=Card)
async def create_card(session: Session = Depends(require_session), user: User = Depends(verify_admin)):
    latest_card = session.exec(select(Card).where(Card.card_id != None).order_by(Card.card_id.desc())).first()
    new_card_id = 1 if latest_card is None else latest_card.card_id + 1
    # admin can create a card without a phone number, and skip the draft state
    card = Card(uuid=str(uuid.uuid4()), card_id=new_card_id)
    database.add_model(session, card)
    preference = CardPreference(uuid=card.uuid)
    database.add_model(session, preference)
    return card


@router.get("", response_model=list[Card])
async def get_cards(session: Session = Depends(require_session), user: User = Depends(verify_admin)):
    return session.exec(select(Card).order_by(Card.created_at.desc())).all()


@router.get("/{uuid}", response_model=CardPublic)
async def get_card(card: Card = Depends(require_card)):
    return card


@router.patch("/{uuid}")
async def update_card(
    mode: Literal["UNSET", "CONFIRMED"],
    card: Card = Depends(require_card),
    session: Session = Depends(require_session),
    user: User = Depends(verify_admin),
):
    if mode == "UNSET":
        card.card_id = None
    elif mode == "CONFIRMED":
        latest_card = session.exec(select(Card).where(Card.card_id != None).order_by(Card.card_id.desc())).first()
        card.card_id = 1 if latest_card is None else latest_card.card_id + 1
    session.commit()
    return {"message": "Card has been updated"}


@router.get("/{uuid}/preference", response_model=CardPreferencePublic)
async def get_preference(
    card: Card = Depends(require_card),
    db_preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
):
    preferences = CardPreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    return preferences


@router.patch("/{uuid}/preference")
async def update_preference(
    preference: CardPreferencePublic,
    card: Card = Depends(require_card_strict),
    db_preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
    user: User = Depends(verify_user_optional),
):
    if user and user.privilege == Privilege.ADMIN:
        update_preference = CardPreferenceUpdate(
            **preference.model_dump(exclude={"character", "background", "frame", "passname"}),
            character_id=preference.character.id if preference.character else None,
            background_id=preference.background.id if preference.background else None,
            frame_id=preference.frame.id if preference.frame else None,
            passname_id=preference.passname.id if preference.passname else None,
        )

    elif (user and db_preference.protect_card and card.username == user.username) or not db_preference.protect_card:
        # user can update the preference if it's not protected, or if the user is the card owner
        update_preference = CardPreferenceUpdate(
            **preference.model_dump(include=["skip_activation", "protect_card"]),
        )

    partial_update_model(session, db_preference, update_preference)
    return {"message": "Preference has been updated"}


@router.get("/{uuid}/accounts", response_model=CardUserPublic)
async def get_account(
    card: Card = Depends(require_card_strict),
    db_account: CardUser = Depends(require_card_user),
    session: Session = Depends(require_session),
):
    def _ser_scores(mpy_scores: list[MpyScore], songs: MaimaiSongs) -> list[ScorePublic]:
        return [
            ScorePublic(
                **(Score.from_mpy(score, db_account.id).model_dump()),
                song_name=song.title,
                level=song.get_difficulty(score.type, score.level_index).level,
            )
            for score in mpy_scores
            if (song := songs.by_id(score.id))
        ]

    songs = await maimai_client.songs()
    scores = MaimaiScores(all=[await Score.as_mpy(score) for score in session.exec(select(Score).where(Score.user_id == db_account.id))], songs=songs)

    return CardUserPublic(
        **db_account.model_dump(exclude={"mai_userid", "mai_rating"}),
        player_rating=db_account.mai_rating,
        player_bests=BestsPublic(
            b35_scores=_ser_scores(scores.scores_b35, songs),
            b15_scores=_ser_scores(scores.scores_b15, songs),
            b35_rating=scores.rating_b35,
            b15_rating=scores.rating_b15,
            all_rating=scores.rating,
        ),
    )


@router.post("/{uuid}/accounts")
async def create_account(
    qrcode: str,
    card: Card = Depends(require_card_strict),
    session: Session = Depends(require_session),
):
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
        log(f"Failed to activate card of {card.card_id}: {repr(e)}", Ansi.LRED)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to activate card")
    await maimai.update_scores(card_user)
    return {"message": "Card account has been activated"}


@router.patch("/{uuid}/accounts")
async def update_accounts(
    card: Card = Depends(require_card_strict),
    db_account: CardUser = Depends(require_card_user),
):
    await maimai.update_scores(db_account)
    return {"message": "Card account has been updated"}


@router.get("/{uuid}/screenshot")
async def get_card_screenshot(
    card: Card = Depends(require_card_strict),
    user: User = Depends(verify_admin),
):
    success, result = await browser.capture_card_screenshot(str(card.uuid))
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"无法生成卡面截图")
    return FileResponse(result, media_type="image/png")


@router.post("/batch/screenshot")
async def get_batch_screenshot(
    uuids: List[str] = Body(...),
    session: Session = Depends(require_session),
    user: User = Depends(verify_admin),
):
    cards = session.exec(select(Card).where(Card.uuid.in_(uuids), Card.card_id != None)).all()
    if len(cards) != len(uuids):
        lost_uuids = set(uuids) - {card.uuid for card in cards}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cards are not found: {', '.join(lost_uuids)}")

    max_id = max(card.card_id for card in cards)
    min_id = min(card.card_id for card in cards)

    _, zip_file = await browser.capture_multiple_screenshot(list(cards))
    return FileResponse(zip_file, media_type="application/zip", filename=f"cards{min_id}-{max_id}.zip")

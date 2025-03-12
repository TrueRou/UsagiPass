import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select
from maimai_py import MaimaiScores, MaimaiSongs, Score as MpyScore
from maimai_py.exceptions import AimeServerError

from usagipass.app import settings
from usagipass.app import database
from usagipass.app.logging import log, Ansi
from usagipass.app.database import partial_update_model, require_session, maimai_client
from usagipass.app.models import Card, CardBests, CardPreference, CardProfile, CardUser, PreferencePublic, PreferenceUpdate, Score, ScorePublic, User
from usagipass.app.usecases import maimai
from usagipass.app.usecases.authorize import verify_admin
from usagipass.app.usecases.accounts import apply_preference


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


@router.delete("/{uuid}")
async def delete_card(card: Card = Depends(require_card), session: Session = Depends(require_session), user: User = Depends(verify_admin)):
    if card.user_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card has already been activated")
    session.delete(card)
    session.commit()
    return {"message": "Card has been deleted"}


@router.patch("/{uuid}/preference")
async def update_preference(
    preference: PreferencePublic,
    db_preference: CardPreference = Depends(require_preference),
    session: Session = Depends(require_session),
    user: User = Depends(verify_admin),
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


@router.post("/{uuid}/accounts")
async def create_card_account(qrcode: str, card: Card = Depends(require_card_strict), session: Session = Depends(require_session)):
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
    return {"message": "Card has been activated"}


@router.get("/{uuid}/profile", response_model=CardProfile)
async def get_profile(
    card: Card = Depends(require_card_strict),
    db_preference: CardPreference = Depends(require_preference),
    db_account: CardUser | None = Depends(require_card_user_optional),
    session: Session = Depends(require_session),
):
    preferences = PreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    card_profile = CardProfile(
        card_id=card.card_id,
        player_rating=db_account.mai_rating if db_account else -1,
        preferences=preferences,
    )
    return card_profile


@router.get("/{uuid}/bests", response_model=CardBests)
async def get_bests(
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
    return CardBests(
        b35_scores=_ser_scores(scores.scores_b35, songs),
        b15_scores=_ser_scores(scores.scores_b15, songs),
        b35_rating=scores.rating_b35,
        b15_rating=scores.rating_b15,
        all_rating=scores.rating,
    )


@router.patch("/{uuid}/bests", response_model=CardBests)
async def update_bests(
    card: Card = Depends(require_card_strict),
    db_account: CardUser = Depends(require_card_user),
    session: Session = Depends(require_session),
):
    await maimai.update_scores(db_account)
    return await get_bests(db_account, session)

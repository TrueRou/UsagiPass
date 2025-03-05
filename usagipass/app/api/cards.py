import asyncio
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from maimai_py import MaimaiScores, MaimaiSongs
from sqlmodel import Session, select
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


def require_card(uuid: str, session: Session = Depends(require_session)) -> Card:
    if card := session.exec(select(Card).where(Card.uuid == uuid)).first():
        return card
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")


def require_preference(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardPreference:
    if preference := session.get(CardPreference, card.cid):
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
    new_uuid = str(uuid.uuid4())
    card = Card(uuid=new_uuid)
    database.add_model(session, card)
    preference = CardPreference(cid=card.cid)
    database.add_model(session, preference)
    return card


@router.post("/accounts")
async def create_card_account(qrcode: str, card: Card = Depends(require_card), session: Session = Depends(require_session)):
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


@router.patch("/preferences")
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


@router.get("/profile", response_model=CardProfile)
async def get_profile(
    card: Card = Depends(require_card),
    db_preference: CardPreference = Depends(require_preference),
    db_account: CardUser | None = Depends(require_card_user_optional),
    session: Session = Depends(require_session),
):
    # we need to trigger the scores updating if the user has not updated for a while
    asyncio.create_task(maimai.update_scores_passive(card))
    preferences = PreferencePublic.model_validate(db_preference)
    apply_preference(preferences, db_preference, session)
    card_profile = CardProfile(
        cid=card.cid,
        player_rating=db_account.mai_rating if db_account else -1,
        preferences=preferences,
    )
    return card_profile


@router.get("/bests", response_model=list[ScorePublic])
async def get_bests(
    db_account: CardUser = Depends(require_card_user),
    session: Session = Depends(require_session),
):
    def _ser_scores(scores: list[Score], songs: MaimaiSongs) -> list[ScorePublic]:
        return [
            ScorePublic(
                **score.model_dump(),
                song_name=song.title,
                level=song.get_difficulty(score.type, score.level_index).level,
            )
            for score in scores
            if (song := songs.by_id(score.song_id))
        ]

    songs = await maimai_client.songs()
    scores = MaimaiScores(all=[await Score.as_mpy(score) for score in session.exec(select(Score).where(Score.user_id == db_account.id))])
    return CardBests(
        b35_scores=_ser_scores(scores.scores_b35, songs),
        b15_scores=_ser_scores(scores.scores_b15, songs),
        b35_rating=scores.rating_b35,
        b15_rating=scores.rating_b15,
        all_rating=scores.rating,
    )

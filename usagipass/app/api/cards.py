from typing import Literal
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session, select
from maimai_py import MaimaiPlates, MaimaiScores, MaimaiSongs, Score as MpyScore, PlateObject
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
    CardScoreUpdateResult,
    CardStatus,
    CardUpdate,
    PlatePublic,
    PreferencePublic,
    PreferenceUpdate,
    Score,
    ScorePublic,
)
from usagipass.app.usecases import fonts, maimai
from usagipass.app.usecases.authorize import verify_admin
from usagipass.app.usecases.accounts import apply_preference


router = APIRouter(prefix="/cards", tags=["cards"])


def require_card(uuid: str = Path(...), session: Session = Depends(require_session)) -> Card:
    if card := session.exec(select(Card).where(Card.uuid == uuid)).first():
        return card
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片未找到")


def require_card_scheduled(card: Card = Depends(require_card)) -> Card:
    if card.status >= CardStatus.SCHEDULED:
        return card
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="卡片尚未安排")


def require_preference(card: Card = Depends(require_card), session: Session = Depends(require_session)) -> CardPreference:
    if preference := session.get(CardPreference, card.uuid):
        return preference
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片尚未初始化")


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
    return {"message": "卡片已更新"}


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
    fonts.check_preference_throw(updates)
    update_preference = PreferenceUpdate(
        **updates.model_dump(exclude={"character", "background", "frame", "passname"}),
        character_id=updates.character.id if updates.character else None,
        background_id=updates.background.id if updates.background else None,
        frame_id=updates.frame.id if updates.frame else None,
        passname_id=updates.passname.id if updates.passname else None,
    )

    partial_update_model(session, preference, update_preference)
    return {"message": "偏好设置已更新"}


@router.post("/{uuid}/accounts")
async def create_account(
    qrcode: str | None = None,
    card: Card = Depends(require_card_scheduled),
    session: Session = Depends(require_session),
):
    if card.status == CardStatus.ACTIVATED and card.account_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="卡片已经绑定过账号")

    if card.status >= CardStatus.SCHEDULED and card.account_id is None and qrcode is None:
        # user skip the activation process, and the card will not bind to any account
        card.status = CardStatus.ACTIVATED
        session.commit()
        return {"message": "卡片已激活"}

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="二维码无效或已过期")
    except Exception as e:
        log(f"Failed to activate card of {card.id}: {repr(e)}", Ansi.LRED)
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="激活卡片失败")
    try:
        await maimai.update_scores(account)  # away from try-except block
    except Exception as e:
        log(f"Failed to update scores of card {card.id}: {repr(e)}", Ansi.LRED)
    return {"message": "卡片账号已创建"}


@router.patch("/{uuid}/accounts", response_model=CardScoreUpdateResult | None)
async def update_accounts(
    card: Card = Depends(require_card),
    db_account: CardAccount = Depends(require_card_account),
):
    if db_account and datetime.utcnow() - db_account.updated_at > timedelta(minutes=15):
        try:
            result = CardScoreUpdateResult(
                player_rating_old=db_account.player_rating,
                player_rating_new=await maimai.update_scores(db_account),
            )
            if result.player_rating_old != result.player_rating_new:
                log(f"Card {db_account.id} has been updated ({result.player_rating_old} -> {result.player_rating_new})", Ansi.LGREEN)
            return result
        except Exception as e:
            log(f"Failed to update scores of card {card.id}: {repr(e)}", Ansi.LRED)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新分数失败")


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
                level=diff.level,
                level_value=diff.level_value,
            )
            for score in mpy_scores
            if (song := songs.by_id(score.id)) and (diff := song.get_difficulty(score.type, score.level_index))
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


@router.get("/{uuid}/plates", response_model=list[PlatePublic])
async def get_plates(
    plate: str,
    attr: Literal["remained", "cleared", "played", "all"] = "remained",
    account: CardAccount = Depends(require_card_account),
    session: Session = Depends(require_session),
):
    def _ser_scores(mpy_scores: list[MpyScore], songs: MaimaiSongs) -> list[ScorePublic]:
        return [
            ScorePublic(
                **(Score.from_mpy(score, account.id).model_dump()),
                song_name=song.title,
                level=diff.level,
                level_value=diff.level_value,
            )
            for score in mpy_scores
            if (song := songs.by_id(score.id)) and (diff := song.get_difficulty(score.type, score.level_index))
        ]

    if account:
        songs = await maimai_client.songs()
        scores = session.exec(select(Score).where(Score.account_id == account.id)).all()
        if len(scores) > 0:
            mplates = MaimaiPlates([await Score.as_mpy(score) for score in scores], plate[0], plate[1:], songs)
            mplate_object: list[PlateObject] = getattr(mplates, attr)
            return [PlatePublic(song=mplate.song, levels=mplate.levels, scores=_ser_scores(mplate.scores, songs)) for mplate in mplate_object]
    return []

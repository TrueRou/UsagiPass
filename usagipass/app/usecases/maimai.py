from asyncio import TaskGroup
from datetime import datetime, timedelta
from sqlmodel import select
from maimai_py import ScoreKind

from usagipass.app.database import session_ctx, maimai_client
from usagipass.app.models import CardAccount, Score, UserAccount
from usagipass.app.usecases import crawler


# trigger the update of the card user's scores
async def update_scores(account: CardAccount) -> int:
    with session_ctx() as session:
        account = session.get(CardAccount, account.id) or account
        new_scores = await maimai_client.scores(account.as_identifier, kind=ScoreKind.ALL, provider=account.as_provider)
        old_scores = session.exec(select(Score).where(Score.account_id == account.id)).all()
        old_scores_dict = {f"{old_score.song_id} {old_score.type} {old_score.level_index}": old_score for old_score in old_scores}

        for new_score in new_scores.scores:
            score_key = f"{new_score.id} {new_score.type} {new_score.level_index}"
            if score_key in old_scores_dict:
                # score already exists in the database, compare the score
                db_score = old_scores_dict[score_key]
                old_score = await db_score.as_mpy()
                if new_score.achievements and not db_score.achievements or new_score is old_score._compare(new_score):
                    # score has changed since the last update, renew the updated_at
                    db_score.achievements = new_score.achievements
                    db_score.fc = new_score.fc
                    db_score.fs = new_score.fs
                    db_score.dx_score = new_score.dx_score
                    db_score.dx_rating = new_score.dx_rating
                    db_score.rate = new_score.rate
                    db_score.updated_at = datetime.utcnow()
            else:
                # score does not exist in the database, add the score
                score = Score.from_mpy(new_score, account.id)
                session.add(score)

        # update the user's rating
        account.player_rating = new_scores.rating
        account.updated_at = datetime.utcnow()
        session.commit()
    return new_scores.rating


# attempt to refresh the usagipass user's rating depends on check_delta
async def update_rating_passive(username: str):
    with session_ctx() as session:
        accounts = session.exec(select(UserAccount).where(UserAccount.username == username))
        async with TaskGroup() as tg:
            for account in accounts:
                if datetime.utcnow() - account.updated_at > timedelta(minutes=30):
                    tg.create_task(crawler.update_rating(account))

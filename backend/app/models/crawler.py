import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlmodel import Field, SQLModel


class CrawlerHistory(SQLModel, table=True):
    __tablename__ = "crawler_histories"

    id: int | None = Field(default=None, primary_key=True)
    game_name: str
    username: str
    account_server: str
    diff_label: str
    success: bool
    scores_num: int
    parsed_json: str = Field(sa_column=Column(MEDIUMTEXT))
    exc_stack: str | None = Field(default=None, sa_column=Column(MEDIUMTEXT))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

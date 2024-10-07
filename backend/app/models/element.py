import datetime
from sqlmodel import Field, SQLModel


class ElementBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    display_name: str
    file_name: str
    source: str = Field(default="builtin")
    uploaded_by: str | None = Field(default=None, foreign_key="users.username")
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Character(ElementBase, table=True):
    __tablename__ = "characters"


class Background(ElementBase, table=True):
    __tablename__ = "backgrounds"


class Frame(ElementBase, table=True):
    __tablename__ = "frames"


class ElementPublic(SQLModel):
    display_name: str
    file_name: str
    source: str

import datetime
from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    kind: str = Field(index=True)
    uploaded_by: str | None = Field(default=None, foreign_key="users.username", index=True)
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class ImagePublic(SQLModel):
    id: int
    name: str
    kind: str

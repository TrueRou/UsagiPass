import datetime
from sqlmodel import Field, SQLModel


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: str = Field(primary_key=True)
    name: str
    kind: str
    sega_name: str | None = Field(default=None, index=True)
    uploaded_by: str | None = Field(default=None, foreign_key="users.username")
    uploaded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class ImageDetail(SQLModel):
    id: str
    name: str
    kind: str
    uploaded_by: str | None


class ImagePublic(SQLModel):
    id: str
    name: str
    uploaded_by: str | None

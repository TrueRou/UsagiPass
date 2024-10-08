import datetime
from sqlmodel import Field, SQLModel

from app.models.image import ImagePublic


class User(SQLModel, table=True):
    __tablename__ = "users"

    username: str = Field(primary_key=True)
    nickname: str
    bind_qq: str
    player_rating: int = Field(default=10000)
    hashed_password: str  # we don't want to store plain diving-fish passwords
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"

    username: str = Field(primary_key=True)
    character_id: str | None = Field(foreign_key="images.id")
    background_id: str | None = Field(foreign_key="images.id")
    frame_id: str | None = Field(foreign_key="images.id")


class UserPreferencePublic(SQLModel):
    character: ImagePublic | None
    background: ImagePublic | None
    frame: ImagePublic | None


class UserProfile(SQLModel):
    username: str
    nickname: str
    player_rating: int
    preferences: UserPreferencePublic

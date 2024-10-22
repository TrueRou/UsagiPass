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


# maimai version, simplified code, character name, friend code, display name, dx rating


class UserPreferenceBase(SQLModel):
    maimai_version: str | None = None
    simplified_code: str | None = None
    character_name: str | None = None
    friend_code: str | None = None
    display_name: str | None = None
    dx_rating: str | None = None
    qr_size: int | None = None


class UserPreferenceUpdate(UserPreferenceBase):
    character_id: str | None = None
    background_id: str | None = None
    frame_id: str | None = None
    passname_id: str | None = None


class UserPreference(UserPreferenceBase, table=True):
    __tablename__ = "user_preferences"

    username: str = Field(primary_key=True)
    character_id: str | None = Field(foreign_key="images.id")
    background_id: str | None = Field(foreign_key="images.id")
    frame_id: str | None = Field(foreign_key="images.id")
    passname_id: str | None = Field(foreign_key="images.id")


class UserPreferencePublic(UserPreferenceBase):
    character: ImagePublic | None = None
    background: ImagePublic | None = None
    frame: ImagePublic | None = None
    passname: ImagePublic | None = None


class UserProfile(SQLModel):
    username: str
    nickname: str
    player_rating: int
    preferences: UserPreferencePublic

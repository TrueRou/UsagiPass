import datetime
from enum import IntEnum, auto
from sqlmodel import Field, SQLModel

from app.models.image import ImagePublic


class AccountServer(IntEnum):
    DIVING_FISH = auto()  # 水鱼查分器
    LXNS = auto()  # 落雪咖啡屋


class User(SQLModel, table=True):
    __tablename__ = "users"

    username: str = Field(primary_key=True)
    prefer_server: AccountServer
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class UserUpdate(SQLModel):
    prefer_server: AccountServer | None = None


class UserAccount(SQLModel, table=True):
    __tablename__ = "user_accounts"

    account_name: str = Field(primary_key=True)
    account_server: AccountServer = Field(primary_key=True)
    account_password: str
    nickname: str
    bind_qq: str = Field(default="")
    player_rating: int = Field(default=10000)
    username: str = Field(index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class UserPreferenceBase(SQLModel):
    maimai_version: str | None = None
    simplified_code: str | None = None
    character_name: str | None = None
    friend_code: str | None = None
    display_name: str | None = None
    dx_rating: str | None = None
    qr_size: int = Field(default=15)
    mask_type: int = Field(default=0)


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


class UserAccountPublic(SQLModel):
    account_name: str
    nickname: str
    player_rating: int


class UserProfile(SQLModel):
    username: str
    prefer_server: AccountServer
    nickname: str
    player_rating: int
    preferences: UserPreferencePublic
    accounts: dict[int, UserAccountPublic]

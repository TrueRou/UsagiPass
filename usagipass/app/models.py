from datetime import datetime
from enum import IntEnum, auto
from sqlmodel import Field, SQLModel
from maimai_py import PlayerIdentifier, ArcadeProvider, Score as MpyScore
from maimai_py.models import FCType, FSType, LevelIndex, RateType, SongType

from usagipass.app import settings
from usagipass.app.database import maimai_client

image_kinds = {
    "background": {"hw": [(768, 1052)]},
    "frame": {"hw": [(768, 1052)]},
    "character": {"hw": [(768, 1052), (1024, 1408)]},
    "mask": {"hw": [(768, 1052), (1024, 1408)]},
    "passname": {"hw": [(338, 112), (363, 110), (374, 105), (415, 115)]},
}

sega_prefixs = ["UI_CardChara_", "UI_CardBase_", "UI_CMA_", "UI_CardCharaMask_"]


class AccountServer(IntEnum):
    DIVING_FISH = auto()  # 水鱼查分器
    LXNS = auto()  # 落雪咖啡屋
    WECHAT = auto()  # 微信小程序


class Privilege(IntEnum):
    BANNED = auto()
    NORMAL = auto()
    ADMIN = auto()


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: str = Field(primary_key=True)
    name: str
    kind: str
    sega_name: str | None = Field(default=None, index=True)
    uploaded_by: str | None = Field(default=None)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ImageDetail(SQLModel):
    id: str
    name: str
    kind: str
    uploaded_by: str | None


class ImagePublic(SQLModel):
    id: str
    name: str
    uploaded_by: str | None


class User(SQLModel, table=True):
    __tablename__ = "users"

    username: str = Field(primary_key=True)
    prefer_server: AccountServer
    privilege: Privilege = Field(default=Privilege.NORMAL, sa_column_kwargs={"server_default": "NORMAL"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PreferenceBase(SQLModel):
    maimai_version: str | None = None
    simplified_code: str | None = None
    character_name: str | None = None
    friend_code: str | None = None
    display_name: str | None = None
    dx_rating: str | None = None
    qr_size: int = Field(default=15)
    mask_type: int = Field(default=0)


class PreferenceUpdate(PreferenceBase):
    character_id: str | None = None
    background_id: str | None = None
    frame_id: str | None = None
    passname_id: str | None = None


class PreferencePublic(PreferenceBase):
    character: ImagePublic | None = None
    background: ImagePublic | None = None
    frame: ImagePublic | None = None
    passname: ImagePublic | None = None


class CardPreferenceUpdate(PreferenceUpdate):
    skip_activation: bool | None = None
    protect_card: bool | None = None


class CardPreferencePublic(PreferencePublic):
    skip_activation: bool | None = None
    protect_card: bool | None = None


class UserPreference(PreferenceBase, table=True):
    __tablename__ = "user_preferences"

    username: str = Field(primary_key=True, foreign_key="users.username")
    character_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    background_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    frame_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    passname_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")


class UserAccountPublic(SQLModel):
    account_name: str
    nickname: str
    player_rating: int


class UserProfile(SQLModel):
    username: str
    prefer_server: AccountServer
    nickname: str
    player_rating: int
    preferences: PreferencePublic
    accounts: dict[int, UserAccountPublic]


class ServerMessage(SQLModel):
    maimai_version: str
    server_motd: str
    author_motd: str


class CardUser(SQLModel, table=True):
    __tablename__ = "card_users"

    id: int = Field(primary_key=True)
    mai_userid: str = Field(unique=True, index=True)
    mai_rating: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def as_identifier(self):
        return PlayerIdentifier(credentials=self.mai_userid)

    @property
    def as_provider(self):
        return ArcadeProvider(settings.arcade_proxy)


class CardPreference(PreferenceBase, table=True):
    __tablename__ = "card_preferences"

    uuid: str = Field(primary_key=True, foreign_key="cards.uuid", ondelete="CASCADE")
    character_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    background_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    frame_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    passname_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    skip_activation: bool = Field(default=False)
    protect_card: bool = Field(default=False)


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    uuid: str = Field(primary_key=True)
    card_id: int | None = Field(default=None, unique=True, index=True)
    user_id: int | None = Field(default=None, foreign_key="card_users.id", ondelete="SET NULL")
    username: str | None = Field(default=None, foreign_key="users.username", ondelete="SET NULL")
    phone_number: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CardProfile(SQLModel):
    card_id: int | None
    user_id: int | None
    player_rating: int
    preferences: CardPreferencePublic


class Score(SQLModel, table=True):
    __tablename__ = "scores"

    id: int | None = Field(default=None, primary_key=True)
    song_id: int = Field(index=True)
    level_index: LevelIndex
    achievements: float | None
    fc: FCType | None
    fs: FSType | None
    dx_score: int | None
    dx_rating: float | None
    rate: RateType
    type: SongType
    user_id: int = Field(foreign_key="card_users.id", index=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def from_mpy(mpy_score: MpyScore, user_id: int):
        return Score(
            song_id=mpy_score.id,
            level_index=mpy_score.level_index,
            achievements=mpy_score.achievements,
            fc=mpy_score.fc,
            fs=mpy_score.fs,
            dx_score=mpy_score.dx_score,
            dx_rating=mpy_score.dx_rating,
            rate=mpy_score.rate,
            type=mpy_score.type,
            user_id=user_id,
        )

    async def as_mpy(self):
        song = (await maimai_client.songs()).by_id(self.song_id)
        return MpyScore(
            id=self.song_id,
            song_name=song.title if song else "Unknown",
            level=song.get_difficulty(self.type, self.level_index).level if song else "Unknown",
            level_index=self.level_index,
            achievements=self.achievements,
            fc=self.fc,
            fs=self.fs,
            dx_score=self.dx_score,
            dx_rating=self.dx_rating,
            rate=self.rate,
            type=self.type,
        )


class ScorePublic(SQLModel):
    song_id: int
    song_name: str
    level: str
    level_index: LevelIndex
    achievements: float | None
    fc: FCType | None
    fs: FSType | None
    dx_score: int | None
    dx_rating: float | None
    rate: RateType
    type: SongType
    user_id: int
    created_at: datetime
    updated_at: datetime


class CardBests(SQLModel):
    b35_scores: list[ScorePublic]
    b15_scores: list[ScorePublic]
    b35_rating: int
    b15_rating: int
    all_rating: int

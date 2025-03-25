from datetime import datetime
from enum import IntEnum, auto
from sqlalchemy import Column, Integer
from sqlmodel import Field, SQLModel
from maimai_py import PlayerIdentifier, ArcadeProvider, Score as MpyScore
from maimai_py.models import FCType, FSType, LevelIndex, RateType, SongType

from usagipass.app import settings
from usagipass.app.database import maimai_client

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

image_kinds = {
    "background": {"hw": [(768, 1052)]},
    "frame": {"hw": [(768, 1052)]},
    "character": {"hw": [(768, 1052), (1024, 1408)]},
    "mask": {"hw": [(768, 1052), (1024, 1408)]},
    "passname": {"hw": [(338, 112), (363, 110), (374, 105), (415, 115)]},
}

sega_prefixs = ["UI_CardChara_", "UI_CardBase_", "UI_CMA_", "UI_CardCharaMask_"]

SQLModel.metadata.naming_convention = convention


class AccountServer(IntEnum):
    DIVING_FISH = auto()  # 水鱼查分器
    LXNS = auto()  # 落雪咖啡屋
    WECHAT = auto()  # 微信小程序


class Privilege(IntEnum):
    BANNED = auto()
    NORMAL = auto()
    ADMIN = auto()


class CardStatus(IntEnum):
    DRAFTED = auto()  # 已建稿 (用户已经设计好卡片，等待管理员确认排产)
    SCHEDULED = auto()  # 已排产 (卡片已经被管理员确认排产，等待创建打印任务)
    CONFIRMED = auto()  # 已确认 (卡片打印任务已经创建，等待生产完成后发货)
    ACTIVATED = auto()  # 已激活 (用户收到卡片，第一次使用并激活卡片)


class ServerMessage(SQLModel):
    maimai_version: str
    server_motd: str
    author_motd: str


class Image(SQLModel, table=True):
    __tablename__ = "images"

    id: str = Field(primary_key=True)
    name: str
    kind: str
    sega_name: str | None = Field(default=None, index=True)
    uploaded_by: str | None = Field(default=None)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ImagePublic(SQLModel):
    id: str
    name: str
    kind: str
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


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True, nullable=False)
    status: CardStatus = Field(default=CardStatus.DRAFTED)
    phone: str | None = Field(default=None, index=True)
    account_id: int | None = Field(default=None, foreign_key="card_accounts.id", ondelete="SET NULL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CardUpdate(SQLModel):
    id: int | None = None
    status: CardStatus | None = None
    phone: str | None = None


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


class UserAccountPublic(SQLModel):
    account_name: str
    nickname: str
    player_rating: int


class PreferenceBase(SQLModel):
    maimai_version: str | None = None
    simplified_code: str | None = None
    character_name: str | None = None
    friend_code: str | None = None
    display_name: str | None = None
    dx_rating: str | None = None
    qr_size: int = Field(default=15)
    mask_type: int = Field(default=0)


class UserPreference(PreferenceBase, table=True):
    __tablename__ = "user_preferences"

    username: str = Field(primary_key=True, foreign_key="users.username")
    character_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    background_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    frame_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    passname_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")


class CardPreference(PreferenceBase, table=True):
    __tablename__ = "card_preferences"

    uuid: str = Field(primary_key=True, foreign_key="cards.uuid", ondelete="CASCADE")
    character_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    background_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    frame_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")
    passname_id: str | None = Field(foreign_key="images.id", ondelete="SET NULL")


class PreferencePublic(PreferenceBase):
    character: ImagePublic | None = None
    background: ImagePublic | None = None
    frame: ImagePublic | None = None
    passname: ImagePublic | None = None


class PreferenceUpdate(PreferenceBase):
    character_id: str | None = None
    background_id: str | None = None
    frame_id: str | None = None
    passname_id: str | None = None


class UserProfile(SQLModel):
    username: str
    prefer_server: AccountServer
    privilege: Privilege
    preferences: PreferencePublic
    accounts: dict[AccountServer, UserAccountPublic]


class Score(SQLModel, table=True):
    __tablename__ = "card_scores"

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
    account_id: int = Field(foreign_key="card_accounts.id", index=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def from_mpy(mpy_score: MpyScore, account_id: int):
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
            account_id=account_id,
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


class BestsPublic(SQLModel):
    b35_scores: list[ScorePublic]
    b15_scores: list[ScorePublic]
    b35_rating: int
    b15_rating: int
    all_rating: int


class CardAccount(SQLModel, table=True):
    __tablename__ = "card_accounts"

    id: int = Field(primary_key=True)
    credentials: str = Field(unique=True, index=True)
    player_rating: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def as_identifier(self):
        return PlayerIdentifier(credentials=self.credentials)

    @property
    def as_provider(self):
        return ArcadeProvider(settings.arcade_proxy)


class CardAccountPublic(SQLModel):
    player_rating: int
    player_bests: BestsPublic
    created_at: datetime


class CardProfile(SQLModel):
    id: int
    uuid: str
    status: CardStatus
    preferences: PreferencePublic
    accounts: CardAccountPublic | None

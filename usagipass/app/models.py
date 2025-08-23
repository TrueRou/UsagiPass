from datetime import datetime
from enum import IntEnum, auto

from sqlmodel import Field, SQLModel

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


class Image(SQLModel, table=True):
    __tablename__ = "images"  # type: ignore

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
    __tablename__ = "users"  # type: ignore

    username: str = Field(primary_key=True)
    prefer_server: AccountServer
    api_token: str | None = Field(default=None, index=True, unique=True)
    privilege: Privilege = Field(default=Privilege.NORMAL, sa_column_kwargs={"server_default": "NORMAL"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserUpdate(SQLModel):
    prefer_server: AccountServer | None = None


class UserAccount(SQLModel, table=True):
    __tablename__ = "user_accounts"  # type: ignore

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
    chara_info_color: str = Field(default="#fee37c", sa_column_kwargs={"server_default": "#fee37c"})
    show_date: bool = Field(default=False)
    player_name_source: str = Field(default="prober")


class UserPreference(PreferenceBase, table=True):
    __tablename__ = "user_preferences"  # type: ignore

    username: str = Field(primary_key=True, foreign_key="users.username")
    character_id: str | None = Field(default=None, foreign_key="images.id", ondelete="SET NULL")
    background_id: str | None = Field(default=None, foreign_key="images.id", ondelete="SET NULL")
    frame_id: str | None = Field(default=None, foreign_key="images.id", ondelete="SET NULL")
    passname_id: str | None = Field(default=None, foreign_key="images.id", ondelete="SET NULL")


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
    api_token: str
    prefer_server: AccountServer
    privilege: Privilege
    preferences: PreferencePublic
    accounts: dict[AccountServer, UserAccountPublic]


class CrawlerResult(SQLModel):
    account_server: int = AccountServer.WECHAT
    success: bool = False
    scores_num: int = 0
    from_rating: int = 0
    to_rating: int = 0
    err_msg: str = ""
    elapsed_time: float = 0.0


class Announcement(SQLModel, table=True):
    __tablename__ = "announcements"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnnouncementRead(SQLModel, table=True):
    __tablename__ = "announcement_reads"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    announcement_id: int = Field(foreign_key="announcements.id", index=True, ondelete="CASCADE")
    username: str = Field(foreign_key="users.username", index=True, ondelete="CASCADE")
    read_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:  # type: ignore
        unique_together = [("announcement_id", "username")]


class AnnouncementCreate(SQLModel):
    title: str
    content: str
    is_active: bool = True


class AnnouncementUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    is_active: bool | None = None


class AnnouncementPublic(SQLModel):
    id: int
    title: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_read: bool = False

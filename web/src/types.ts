type Kind = "background" | "frame" | "character" | "passname" | "mask"

enum Privilege {
    BANNED = 1,
    NORMAL = 2,
    ADMIN = 3
}

enum AccountServer {
    DIVINGFISH = 1,
    LXNS = 2,
    WECHAT = 3
}

enum CardStatus {
    DRAFTED = 1,
    SCHEDULED = 2,
    CONFIRMED = 3,
    ACTIVATED = 4
}

enum LevelIndex {
    BASIC = 0,
    ADVANCED = 1,
    EXPERT = 2,
    MASTER = 3,
    ReMASTER = 4
}

enum FCType {
    APP = 0,
    AP = 1,
    FCP = 2,
    FC = 3
}

enum FSType {
    SYNC = 0,
    FS = 1,
    FSP = 2,
    FSD = 3,
    FSDP = 4
}

enum RateType {
    SSSP = 0,
    SSS = 1,
    SSP = 2,
    SS = 3,
    SP = 4,
    S = 5,
    AAA = 6,
    AA = 7,
    A = 8,
    BBB = 9,
    BB = 10,
    B = 11,
    C = 12,
    D = 13
}

enum SongType {
    STANDARD = "standard",
    DX = "dx",
    UTAGE = "utage"
}

interface Image {
    id: string;
    name: string;
    kind: Kind;
    uploaded_by?: string;
}

interface Preference {
    character: Image;
    background: Image;
    frame: Image;
    passname: Image;
    maimai_version?: string;
    simplified_code?: string;
    character_name?: string;
    friend_code?: string;
    display_name?: string;
    dx_rating?: string;
    qr_size?: number;
    mask_type?: number;
}

interface UserAccount {
    account_name: string;
    nickname: string;
    player_rating: number;
}

interface UserProfile {
    username: string;
    prefer_server: AccountServer;
    privilege: Privilege;
    preferences: Preference;
    accounts: Record<AccountServer, UserAccount>;
}

interface ServerMessage {
    maimai_version: string;
    server_motd: string;
    author_motd: string;
}

interface CrawlerResult {
    account_server: number;
    success: boolean;
    scores_num: number;
    from_rating: number;
    to_rating: number;
    err_msg: string;
    elapsed_time: number;
}

interface Score {
    song_id: number;
    song_name: string;
    level: string;
    level_index: LevelIndex;
    achievements: number | null;
    fc: FCType | null;
    fs: FSType | null;
    dx_score: number | null;
    dx_rating: number | null;
    rate: RateType;
    type: SongType;
}

interface Card {
    id: number;
    uuid: string;
    status: CardStatus;
    phone?: string;
    account_id?: number;
    created_at: string;
    updated_at: string;
}

interface Bests {
    b35_scores: Score[];
    b15_scores: Score[];
    b35_rating: number;
    b15_rating: number;
    all_rating: number;
}

interface CardAccount {
    player_rating: number;
    player_bests: Bests;
    created_at: string;
}

interface CardProfile {
    id: number;
    uuid: string;
    status: CardStatus;
    preferences: Preference;
    accounts?: CardAccount;
}

type CardStatusEntities = "tag" | "color"

const CardStatusMap: Record<CardStatus, Record<CardStatusEntities, string>> = {
    [CardStatus.DRAFTED]: {
        tag: "草稿",
        color: "bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full font-bold"
    },
    [CardStatus.SCHEDULED]: {
        tag: "已付款",
        color: "bg-orange-100 text-orange-800 px-2 py-1 rounded-full font-bold"
    },
    [CardStatus.CONFIRMED]: {
        tag: "已确认",
        color: "bg-green-100 text-green-800 px-2 py-1 rounded-full font-bold"
    },
    [CardStatus.ACTIVATED]: {
        tag: "已激活",
        color: "bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-bold"
    }
}

export { Privilege, AccountServer, CardStatus, CardStatusMap };
export type { Kind, Preference, UserAccount, UserProfile, ServerMessage, CrawlerResult, Score, Card, Bests, CardProfile, CardAccount, Image, FCType, FSType, RateType, SongType, LevelIndex };

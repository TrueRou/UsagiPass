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

enum ViewMode {
    LIST = 'list',
    TILE = 'tile',
}

enum TileDisplayMode {
    NONE = "none",
    RATING = "rating",
    ACHIEVEMENT = "achievement",
    FC = "fc",
    FS = "fs",
    DX_RATING = "dx_rating",
    LEVEL_VALUE = "level_value",
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

enum TaskStatus {
    PENDING = 1,
    RUNNING = 2,
    COMPLETED = 3,
    FAILED = 4
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
    level_value: number;
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

interface CardScoreUpdateResult {
    player_rating_old: number;
    player_rating_new: number;
}

interface Task {
    id: string;
    task_type: string;
    status: TaskStatus;
    created_by: string;
    created_at: string;
    updated_at: string;
    error_message: string | null;
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

const TaskStatusMap = {
    [TaskStatus.PENDING]: { tag: '等待中', color: 'text-gray-500 font-medium' },
    [TaskStatus.RUNNING]: { tag: '处理中', color: 'text-blue-500 font-medium' },
    [TaskStatus.COMPLETED]: { tag: '已完成', color: 'text-green-500 font-medium' },
    [TaskStatus.FAILED]: { tag: '失败', color: 'text-red-500 font-medium' }
};

// FC状态映射
const FCTypeMap: Record<FCType, string> = {
    [FCType.APP]: 'AP+',
    [FCType.AP]: 'AP',
    [FCType.FCP]: 'FC+',
    [FCType.FC]: 'FC'
};

// FS状态映射
const FSTypeMap: Record<FSType, string> = {
    [FSType.SYNC]: 'SYNC',
    [FSType.FS]: 'FS',
    [FSType.FSP]: 'FS+',
    [FSType.FSD]: 'FSD',
    [FSType.FSDP]: 'FSD+'
};

// 成绩等级映射
const RateTypeMap: Record<RateType, string> = {
    [RateType.SSSP]: 'SSS+',
    [RateType.SSS]: 'SSS',
    [RateType.SSP]: 'SS+',
    [RateType.SS]: 'SS',
    [RateType.SP]: 'S+',
    [RateType.S]: 'S',
    [RateType.AAA]: 'AAA',
    [RateType.AA]: 'AA',
    [RateType.A]: 'A',
    [RateType.BBB]: 'BBB',
    [RateType.BB]: 'BB',
    [RateType.B]: 'B',
    [RateType.C]: 'C',
    [RateType.D]: 'D'
};

export { Privilege, AccountServer, CardStatus, CardStatusMap, TaskStatusMap, TaskStatus, ViewMode, TileDisplayMode, FCTypeMap, FSTypeMap, RateTypeMap };
export type { Kind, Preference, UserAccount, UserProfile, ServerMessage, CrawlerResult, Score, Card, Bests, CardProfile, CardAccount, Image, FCType, FSType, RateType, SongType, LevelIndex, CardScoreUpdateResult, CardStatusEntities, Task };

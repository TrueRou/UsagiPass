type Kind = "background" | "frame" | "character" | "passname" | "mask"
type Server = "divingfish" | "lxns"

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

interface ImagePublic {
    id: string;
    name: string;
    uploaded_by?: string;
}

interface ImageDetail extends ImagePublic {
    kind: Kind;
}

interface PreferencePublic {
    character: ImagePublic;
    background: ImagePublic;
    frame: ImagePublic;
    passname: ImagePublic;
    maimai_version?: string;
    simplified_code?: string;
    character_name?: string;
    friend_code?: string;
    display_name?: string;
    dx_rating?: string;
    qr_size?: number;
    mask_type?: number;
}

interface UserAccountPublic {
    account_name: string;
    nickname: string;
    player_rating: number;
}

interface UserProfile {
    username: string;
    prefer_server: number;
    nickname: string;
    player_rating: number;
    preferences: PreferencePublic;
    accounts: Record<string, UserAccountPublic>;
}

interface Card {
    uuid: string;
    card_id?: number;
    user_id?: number;
    phone_number?: string;
    created_at: string;
}

interface CardProfile {
    card_id: number;
    player_rating: number;
    preferences: PreferencePublic;
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

interface ScorePublic {
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
    user_id: number;
    created_at: string;
    updated_at: string;
}

interface CardBests {
    b35_scores: ScorePublic[];
    b15_scores: ScorePublic[];
    b35_rating: number;
    b15_rating: number;
    all_rating: number;
}

const mapServerId: Record<Server, number> = {
    "divingfish": 1,
    "lxns": 2,
};

export { mapServerId };
export type { Kind, Server, ImagePublic, ImageDetail, PreferencePublic, UserAccountPublic, UserProfile, Card, CardProfile, ServerMessage, CrawlerResult, ScorePublic, CardBests };

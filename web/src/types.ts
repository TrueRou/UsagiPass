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
    chara_info_color: string;
}

interface UserAccount {
    account_name: string;
    nickname: string;
    player_rating: number;
}

interface UserProfile {
    username: string;
    api_token: string;
    prefer_server: AccountServer;
    privilege: Privilege;
    preferences: Preference;
    accounts: Record<AccountServer, UserAccount>;
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


export { Privilege, AccountServer };
export type { Kind, Preference, UserAccount, UserProfile, CrawlerResult, Image };

interface ImagePublic {
    id: string;
    name: string;
    uploaded_by?: string;
}

interface ImageDetail extends ImagePublic {
    kind: string;
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
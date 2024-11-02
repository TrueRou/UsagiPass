interface ImagePublic {
    id: string;
    name: string;
    uploaded_by?: string;
}

interface ImageDetail extends ImagePublic {
    kind: string;
}

interface UserPreferencePublic {
    character: ImagePublic;
    background: ImagePublic;
    frame: ImagePublic;
    passname: ImagePublic;
    maimai_version?: string;
    simplified_code?: string;
    character_name?: string;
    friend_code?: string;
    display_name?: string;
    dx_rating?: number;
    qr_size?: number;
    mask_type?: number;
}

interface UserProfile {
    username: string;
    nickname: string;
    player_rating: number;
    preferences: UserPreferencePublic;
}

interface ServerMessage {
    maimai_version: string;
    server_motd: string;
    author_motd: string;
}
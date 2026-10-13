/**
 * OAuth 令牌响应（leporidae /oauth/token，RFC 6749）
 */
export interface OAuthTokenResponse {
    /** 访问令牌 */
    access_token: string
    /** 刷新令牌（每次刷新轮换） */
    refresh_token: string
    /** 令牌类型 */
    token_type: string
    /** 访问令牌过期时间（秒） */
    expires_in: number
}

/**
 * 用户响应
 */
export interface UserResponse {
    /** 用户 ID */
    id: string
    /** 用户名 */
    username: string
    /** 邮箱 */
    email: string
}

export interface Metadata {
    key: string
    value: string
    updatedAt: Date | string
    updatedBy: string | null
}

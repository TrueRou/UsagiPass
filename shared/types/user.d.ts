export enum AuthStrategy {
    LOCAL = "LOCAL",
    DIVING_FISH = "DIVING_FISH",
    LXNS = "LXNS",
}

/**
 * 用户注册请求
 */
export interface UserCreateRequest {
    /** 用户名 */
    username: string
    /** 密码 */
    password: string
    /** 手机号 */
    email: string
}

/**
 * 用户令牌创建请求
 */
export interface UserAuthRequest {
    /** 用户名 */
    username: string
    /** 密码 */
    password: string
    /** 认证策略 */
    strategy?: AuthStrategy
    /** 刷新令牌 */
    refresh_token?: string
}

/**
 * 用户令牌响应
 */
export interface UserAuthResponse {
    /** 访问令牌 */
    access_token: string
    /** 刷新令牌 */
    refresh_token: string
    /** 令牌类型 */
    token_type: string
    /** 过期时间（秒） */
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
    /** 用户权限 */
    permissions: string[]
}

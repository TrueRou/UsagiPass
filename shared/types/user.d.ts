/**
 * 用户注册请求
 */
export interface UserRegisterRequest {
    /** 用户名 */
    username: string
    /** 密码 */
    password: string
    /** 手机号 */
    email: string
}

/**
 * 用户登录请求
 */
export interface UserLoginRequest {
    /** 用户名 */
    username: string
    /** 密码 */
    password: string
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

import { joinURL } from 'ufo'

/** leporidae 公开运行时配置（GET /platform/config） */
interface PlatformConfig {
    uc_public_url: string
    fe_public_url: string
}

const PLATFORM_CONFIG_TTL_MS = 10 * 60 * 1000
let platformConfigCache: { value: PlatformConfig, expiresAt: number } | undefined

/** 获取 leporidae 公开配置（官网地址等），进程内缓存 10 分钟，不在本地配置文件中维护 */
export async function getPlatformConfig(): Promise<PlatformConfig> {
    if (platformConfigCache && platformConfigCache.expiresAt > Date.now())
        return platformConfigCache.value
    const response = await $fetch<{ data: PlatformConfig }>(joinURL(useRuntimeConfig().leporidae.baseURL, '/platform/config'))
    platformConfigCache = { value: response.data, expiresAt: Date.now() + PLATFORM_CONFIG_TTL_MS }
    return response.data
}

/** 以 OAuth refresh token 轮换令牌（旧 refresh token 立即作废，调用方须写回 session） */
export async function refreshTokens(refreshToken: string): Promise<OAuthTokenResponse> {
    const config = useRuntimeConfig()
    return await $fetch<OAuthTokenResponse>(joinURL(config.leporidae.baseURL, '/oauth/token'), {
        method: 'POST',
        body: new URLSearchParams({
            grant_type: 'refresh_token',
            refresh_token: refreshToken,
            client_id: config.oauth.oidc.clientId,
            client_secret: config.oauth.oidc.clientSecret,
        }),
    })
}

/** 吊销 refresh token（登出时调用；令牌无效时 leporidae 同样返回成功） */
export async function revokeTokens(refreshToken: string): Promise<void> {
    const config = useRuntimeConfig()
    await $fetch(joinURL(config.leporidae.baseURL, '/oauth/revoke'), {
        method: 'POST',
        body: new URLSearchParams({
            token: refreshToken,
            client_id: config.oauth.oidc.clientId,
            client_secret: config.oauth.oidc.clientSecret,
        }),
    })
}

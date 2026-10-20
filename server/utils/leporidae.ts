import { createHash } from 'node:crypto'
import { joinURL } from 'ufo'

/** 以 OAuth refresh token 轮换令牌（旧 refresh token 立即作废，调用方须写回 session） */
export async function refreshTokens(refreshToken: string): Promise<OAuthTokenResponse> {
    const config = useRuntimeConfig()
    return await $fetch<OAuthTokenResponse>(joinURL(config.leporidae.baseURL, '/oauth/token'), {
        method: 'POST',
        body: new URLSearchParams({
            grant_type: 'refresh_token',
            refresh_token: refreshToken,
            refresh_request_id: createHash('sha256').update(refreshToken).digest('hex'),
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

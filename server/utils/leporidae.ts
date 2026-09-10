import { joinURL } from 'ufo'

export async function refreshTokens(refreshToken: string): Promise<UserAuthResponse> {
    const proxyUrl = useRuntimeConfig().leporidae.baseURL
    return await $fetch<UserAuthResponse>(joinURL(proxyUrl, '/auth/refresh'), {
        method: 'POST',
        body: { refresh_token: refreshToken },
    })
}

import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const proxyUrl = useRuntimeConfig().leporid.baseURL

    const path = event.path.replace(/^\/api\//, '')
    const target = joinURL(proxyUrl, path)
    const headers: Record<string, string> = {}

    if (session.secure) {
        // 如果过期了，尝试刷新令牌
        if (session.secure.expiresAt < Date.now()) {
            await $fetch<UserAuthResponse>('/api/auth/token', {
                method: 'POST',
                ignoreResponseError: true,
                query: {
                    grant_type: 'refresh_token',
                    refresh_token: session.secure.refreshToken,
                },
                async onResponse({ response }) {
                    if (response.status === 200) {
                        await setUserSession(event, {
                            user: session.user,
                            secure: {
                                accessToken: response._data.access_token,
                                refreshToken: response._data.refresh_token,
                                expiresAt: Date.now() + (response._data.expires_in * 1000),
                            },
                        })
                    }
                    else if (response.status === 401) {
                        await clearUserSession(event)
                    }
                },
            })
        }
        // 如果令牌不存在，使用后端访问令牌进行代理请求
        const reqAuthorization = getHeader(event, 'authorization')
        const curAuthorization = `Bearer ${session.secure.accessToken}`
        headers.Authorization = reqAuthorization || curAuthorization
    }

    {
        const method = event.node?.req?.method ?? 'UNKNOWN'
        const userId = session?.user?.username ?? 'anonymous'
        const safeUrl = event.node.req.url?.split('?')[0] ?? ''

        console.info(`[proxy] ${new Date().toISOString()} ${method} ${safeUrl} -> ${proxyUrl} user=${userId}`)
    }

    return proxyRequest(event, target, { headers })
})

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
                body: new URLSearchParams({
                    grant_type: 'refresh_token',
                    refresh_token: session.secure.refreshToken,
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
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
            // 刷新后重新读取 session，避免使用刷新前已过期的旧 token
            const freshSession = await getUserSession(event)
            // refresh token 也已失效，session 已被清除，拒绝本次请求
            if (!freshSession.secure) {
                throw createError({ statusCode: 401, statusMessage: '会话已过期，请重新登录' })
            }
            // 使用刷新后的新 token
            const reqAuthorization = getHeader(event, 'authorization')
            headers.Authorization = reqAuthorization || `Bearer ${freshSession.secure.accessToken}`
        }
        else {
            // token 未过期，直接使用当前 token
            const reqAuthorization = getHeader(event, 'authorization')
            headers.Authorization = reqAuthorization || `Bearer ${session.secure.accessToken}`
        }
    }

    {
        const method = event.node?.req?.method ?? 'UNKNOWN'
        const userId = session?.user?.username ?? 'anonymous'
        const safeUrl = event.node.req.url?.split('?')[0] ?? ''

        console.info(`[proxy] ${new Date().toISOString()} ${method} ${safeUrl} -> ${proxyUrl} user=${userId}`)
    }

    return proxyRequest(event, target, { headers })
})

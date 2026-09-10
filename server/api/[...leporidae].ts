import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const config = useRuntimeConfig()
    const proxyUrl = config.leporidae.baseURL
    const reqAuthorization = getHeader(event, 'authorization')

    const path = event.path.replace(/^\/api\//, '')
    const target = joinURL(proxyUrl, path)

    const method = event.node?.req?.method ?? 'UNKNOWN'
    const userId = session?.user?.username ?? 'anonymous'
    const safeUrl = event.node.req.url?.split('?')[0] ?? ''

    console.info(`[proxy] ${new Date().toISOString()} ${method} ${safeUrl} -> ${proxyUrl} user=${userId}`)

    const buildHeaders = (accessToken?: string): Record<string, string> => {
        const headers: Record<string, string> = {
            'x-developer-token': config.leporidae.developerToken,
        }
        if (reqAuthorization)
            headers.Authorization = reqAuthorization
        else if (accessToken)
            headers.Authorization = `Bearer ${accessToken}`
        return headers
    }

    let val = await proxyRequest(event, target, { headers: buildHeaders(session.secure?.accessToken) })

    if (event.node.res.statusCode === 401 && !reqAuthorization && session.secure?.refreshToken) {
        console.info(`[auth] ${new Date().toISOString()} access token expired for user=${userId}, attempting refresh.`)
        try {
            const tokens = await refreshTokens(session.secure.refreshToken)
            await setUserSession(event, {
                ...session,
                secure: {
                    accessToken: tokens.access_token,
                    refreshToken: tokens.refresh_token,
                },
            })
            console.info(`[auth] ${new Date().toISOString()} token refreshed for user=${userId}, retrying request.`)
            val = await proxyRequest(event, target, { headers: buildHeaders(tokens.access_token) })
        }
        catch {
            console.warn(`[auth] ${new Date().toISOString()} refresh failed for user=${userId}, clearing session.`)
            await clearUserSession(event)
            return val
        }
    }

    if (event.node.res.statusCode === 401 && !reqAuthorization) {
        console.warn(`[auth] ${new Date().toISOString()} 401 Unauthorized for ${method} ${safeUrl} user=${userId}, clearing session.`)
        await clearUserSession(event)
    }

    return val
})

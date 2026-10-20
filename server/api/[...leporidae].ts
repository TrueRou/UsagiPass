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

    const refreshToken = session.secure?.refreshToken
    const fetch = !reqAuthorization && refreshToken
        ? createOAuthProxyFetch({
                refresh: () => refreshTokens(refreshToken),
                save: async (tokens) => {
                    await setUserSession(event, {
                        ...session,
                        secure: {
                            accessToken: tokens.access_token,
                            refreshToken: tokens.refresh_token,
                        },
                    })
                },
                clear: async () => {
                    console.warn(`[auth] refresh token invalid for user=${userId}, clearing session.`)
                    await clearUserSession(event)
                },
            })
        : undefined

    return proxyRequest(event, target, { headers: buildHeaders(session.secure?.accessToken), fetch })
})

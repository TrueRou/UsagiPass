import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const proxyUrl = useRuntimeConfig().leporid.baseURL
    const reqAuthorization = getHeader(event, 'authorization')

    const path = event.path.replace(/^\/api\//, '')
    const target = joinURL(proxyUrl, path)
    const headers: Record<string, string> = {}

    if (session.secure) {
        headers.Authorization = reqAuthorization || `Bearer ${session.secure.accessToken}`
    }

    const method = event.node?.req?.method ?? 'UNKNOWN'
    const userId = session?.user?.username ?? 'anonymous'
    const safeUrl = event.node.req.url?.split('?')[0] ?? ''

    console.info(`[proxy] ${new Date().toISOString()} ${method} ${safeUrl} -> ${proxyUrl} user=${userId}`)

    const val = await proxyRequest(event, target, { headers })

    if (event.node.res.statusCode === 401 && !reqAuthorization) {
        console.warn(`[auth] ${new Date().toISOString()} 401 Unauthorized for ${method} ${safeUrl} user=${userId}, clearing session.`)
        await clearUserSession(event)
    }

    return val
})

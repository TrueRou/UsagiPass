import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const proxyUrl = useRuntimeConfig().otoge.baseURL

    const path = event.path.replace(/^\/api\/otoge/, '')
    const target = joinURL(proxyUrl, path)

    {
        const method = event.node?.req?.method ?? 'UNKNOWN'
        const safeUrl = event.node.req.url?.split('?')[0] ?? ''

        console.info(`[proxy] ${new Date().toISOString()} ${method} ${safeUrl} -> ${proxyUrl}`)
    }

    return proxyRequest(event, target)
})

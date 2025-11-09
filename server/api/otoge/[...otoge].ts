import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const proxyUrl = useRuntimeConfig().otoge.baseURL

    const path = event.path.replace(/^\/api\/otoge/, '')
    const target = joinURL(proxyUrl, path)

    return proxyRequest(event, target)
})

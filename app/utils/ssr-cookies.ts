import type { H3Event } from 'h3'
import { appendResponseHeader } from 'h3'

/** Each SSR render owns its cookie jar; never share cookies between users. */
export function createSsrCookieForwarder(event: H3Event) {
    const cookies = new Map((event.node.req.headers.cookie || '').split(';').map(cookie => cookie.trim()).filter(Boolean).map((cookie) => {
        const index = cookie.indexOf('=')
        return [cookie.slice(0, index), cookie.slice(index + 1)]
    }))

    return {
        requestCookie: () => [...cookies].map(([name, value]) => `${name}=${value}`).join('; '),
        onResponse(headers: Headers) {
            for (const cookie of headers.getSetCookie()) {
                appendResponseHeader(event, 'set-cookie', cookie)
                const pair = cookie.split(';')[0]!
                const index = pair.indexOf('=')
                const name = pair.slice(0, index)
                const value = pair.slice(index + 1)
                if (value)
                    cookies.set(name, value)
                else
                    cookies.delete(name)
            }
        },
    }
}

import type { OAuthTokenResponse } from '../../shared/types/user'

interface OAuthProxyOptions {
    refresh: () => Promise<OAuthTokenResponse>
    save: (tokens: OAuthTokenResponse) => Promise<void>
    clear: () => Promise<void>
    fetch?: typeof globalThis.fetch
}

/** Intercept the upstream response BEFORE h3 writes headers or streams its body. */
export function createOAuthProxyFetch(options: OAuthProxyOptions): typeof globalThis.fetch {
    const fetch = options.fetch ?? globalThis.fetch
    return async (input, init) => {
        const response = await fetch(input, init)
        if (response.status !== 401)
            return response

        let tokens: OAuthTokenResponse
        try {
            tokens = await options.refresh()
        }
        catch (error) {
            const failure = error as { statusCode?: number, data?: { error?: string } }
            if (failure.statusCode === 400 && failure.data?.error === 'invalid_grant') {
                await options.clear()
                return response
            }

            // A timeout, invalid client configuration or upstream outage is not a logout.
            await response.body?.cancel()
            console.warn('[auth] OAuth refresh temporarily unavailable', {
                statusCode: failure.statusCode,
                error: failure.data?.error,
            })
            return Response.json({ code: 503, message: '登录状态刷新暂时失败，请稍后重试。' }, { status: 503 })
        }

        await response.body?.cancel()
        await options.save(tokens)
        const headers = new Headers(init?.headers)
        headers.set('authorization', `Bearer ${tokens.access_token}`)
        // proxyRequest buffers the request body by default, so POST/PUT can also be replayed.
        // Do not include this fetch in the refresh catch: a business API failure is not a logout.
        return fetch(input, { ...init, headers })
    }
}

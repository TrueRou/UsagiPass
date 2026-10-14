import type { H3Event } from 'h3'
import { joinURL, withQuery } from 'ufo'

const REDIRECT_COOKIE = 'usagipass-login-redirect'

/** 仅允许站内路径，避免开放重定向 */
function safeRedirect(value: unknown): string {
    return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/auth/')
        ? value
        : '/'
}

async function fail(event: H3Event, message: string) {
    deleteCookie(event, REDIRECT_COOKIE)
    console.warn(`[auth] ${new Date().toISOString()} UsagiLab OAuth login failed: ${message}`)
    return sendRedirect(event, withQuery('/auth/login', { error: message }))
}

/**
 * UsagiLab 账号登录（授权码 + PKCE），由 nuxt-auth-utils 的通用 OIDC handler 完成：
 * 首次请求跳转官网授权页，回调时校验 state 并以 client 凭据 + code_verifier 换取令牌。
 * 令牌只保存在服务端加密 session（secure）中，刷新见 server/utils/leporidae.ts。
 */
export default defineEventHandler(async (event) => {
    const config = useRuntimeConfig(event)
    const query = getQuery(event)

    if (!query.code && !query.error)
        setCookie(event, REDIRECT_COOKIE, safeRedirect(query.redirect), { httpOnly: true, sameSite: 'lax', maxAge: 600, path: '/' })

    const handler = defineOAuthOidcEventHandler<{ data: UserResponse }>({
        config: {
            // 回调地址固定为本站：由 public.URL 拼接，无需单独配置 NUXT_OAUTH_OIDC_REDIRECT_URL
            redirectURL: joinURL(config.public.URL, '/api/nuxt/auth/leporidae'),
            openidConfig: {
                authorization_endpoint: joinURL(config.leporidae.fePublicURL, '/oauth/authorize'),
                token_endpoint: joinURL(config.leporidae.baseURL, '/oauth/token'),
                userinfo_endpoint: joinURL(config.leporidae.baseURL, '/users/me'),
            },
            // ?prompt=create：未登录时官网直接展示注册页（OIDC prompt=create）
            params: query.prompt === 'create' ? { authorization_endpoint: { prompt: 'create' } } : undefined,
        },
        async onSuccess(event, { user, tokens }) {
            if (!tokens.refresh_token)
                return fail(event, '登录失败：未返回刷新令牌')

            await setUserSession(event, {
                user: {
                    id: user.data.id,
                    username: user.data.username,
                    email: user.data.email,
                },
                secure: {
                    accessToken: tokens.access_token,
                    refreshToken: tokens.refresh_token,
                },
            })
            const redirect = safeRedirect(getCookie(event, REDIRECT_COOKIE))
            deleteCookie(event, REDIRECT_COOKIE)
            console.info(`[auth] ${new Date().toISOString()} user=${user.data.username} logged in via UsagiLab OAuth.`)
            return sendRedirect(event, redirect)
        },
        onError(event, error) {
            return fail(event, query.error === 'access_denied' ? '已取消授权' : (error.message || '登录失败'))
        },
    })

    try {
        return await handler(event)
    }
    catch (error: any) {
        // 令牌端点的 400（如授权码过期）不经过 onError，直接抛出
        return fail(event, error?.data?.error_description ?? error?.message ?? '登录失败')
    }
})

const PENDING_PREFIX = 'usagipass:prober-oauth:'
const PENDING_TTL_MS = 10 * 60 * 1000

interface ProberOAuthPending {
    provider: string
    createdAt: number
}

/** 发起查分器 OAuth 授权：申请授权页地址，记录 state 后跳转（离开当前页面） */
export async function startProberOAuth(provider: string) {
    const authorization = await useNuxtApp().$leporidae<{ authorize_url: string, state: string }>(`/api/nuxt/oauth/${provider}/authorize`, {
        method: 'POST',
    })
    const pending: ProberOAuthPending = { provider, createdAt: Date.now() }
    // 回调时核对 state 确实由本浏览器发起；使用 localStorage 以兼容在新标签页中完成授权的情况
    localStorage.setItem(PENDING_PREFIX + authorization.state, JSON.stringify(pending))
    window.location.assign(authorization.authorize_url)
}

/** 取出并删除 state 对应的本地记录；不存在、已过期或查分器不一致时返回 false */
export function consumeProberOAuthState(state: string, provider: string) {
    const key = PENDING_PREFIX + state
    const raw = localStorage.getItem(key)
    localStorage.removeItem(key)
    if (!raw)
        return false
    try {
        const pending = JSON.parse(raw) as ProberOAuthPending
        return pending.provider === provider && Date.now() - pending.createdAt <= PENDING_TTL_MS
    }
    catch {
        return false
    }
}

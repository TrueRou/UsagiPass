/** 支持 OAuth 授权绑定的查分器（与 tbl_server.identifier 一致） */
export const PROBER_OAUTH_SERVERS = ['divingfish', 'lxns'] as const

export type ProberOAuthServer = typeof PROBER_OAUTH_SERVERS[number]

/** OAuth 授权句柄的前缀；旧的 Import-Token / 个人 API 密钥不带该前缀 */
export const PROBER_OAUTH_CREDENTIAL_PREFIX = 'oauth$'

export function isProberOAuthServer(identifier?: string | null): identifier is ProberOAuthServer {
    return PROBER_OAUTH_SERVERS.includes(identifier as ProberOAuthServer)
}

export function isProberOAuthCredential(credentials?: string | null) {
    return !!credentials?.startsWith(PROBER_OAUTH_CREDENTIAL_PREFIX)
}

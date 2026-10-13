/** 作废查分器 OAuth 授权（尽力而为：失败只记日志，不影响本地删除） */
export async function revokeProberOAuthCredential(credentials: string) {
    if (!isProberOAuthCredential(credentials))
        return
    try {
        await $fetch('/api/maimai/oauth/revoke', {
            method: 'POST',
            body: { credential: credentials },
        })
    }
    catch (error) {
        console.warn(`[oauth] ${new Date().toISOString()} failed to revoke prober oauth grant: ${error}`)
    }
}

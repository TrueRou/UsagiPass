/** 登出：先在 leporidae 吊销 refresh token，再清除本地 session */
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    if (session.secure?.refreshToken) {
        try {
            await revokeTokens(session.secure.refreshToken)
        }
        catch (error) {
            // 吊销失败不阻塞登出：refresh token 会在过期或下次轮换时失效
            console.warn(`[auth] ${new Date().toISOString()} revoke failed for user=${session.user?.username ?? 'anonymous'}: ${error}`)
        }
    }
    await clearUserSession(event)
    return { code: 200, message: '已退出登录', data: {} }
})

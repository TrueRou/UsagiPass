export default defineNuxtRouteMiddleware(async (_to, _from) => {
    const { loggedIn, ready, fetch } = useUserSession()

    // .client.vue 页面不走 SSR，session 状态需要客户端主动拉取；
    // 首次导航时 ready 为 false，先等待 fetch 完成再判断登录态
    if (!ready.value) {
        await fetch()
    }

    if (loggedIn.value === false) {
        if (import.meta.client) {
            const { addNotification } = useNotificationsStore()
            addNotification({
                type: 'warning',
                message: '请登录以访问此页面。',
            })
        }
        return navigateTo(`/auth/login?redirect=${encodeURIComponent(_to.fullPath)}`)
    }
})

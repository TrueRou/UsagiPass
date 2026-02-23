export default defineNuxtRouteMiddleware(async (_to, _from) => {
    const { loggedIn } = useUserSession()

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

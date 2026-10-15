export default defineNuxtRouteMiddleware((_to, _from) => {
    const { loggedIn } = useUserSession()
    const guestCookie = useCookie<boolean>('guest')

    // Redirect to login if not authenticated and not in guest mode
    if (loggedIn.value === false && guestCookie.value !== true) {
        return navigateTo('/auth/login')
    }
})

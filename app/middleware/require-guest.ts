export default defineNuxtRouteMiddleware((_from, _to) => {
    const { loggedIn } = useUserSession()
    const guestCookie = useCookie<boolean>('guest')

    // Redirect to login if not authenticated and not in guest mode
    if (loggedIn.value === false && guestCookie.value !== true) {
        return navigateTo('/auth/login')
    }
})

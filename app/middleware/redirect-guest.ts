export default defineNuxtRouteMiddleware((from, to) => {
    // Don't redirect if already on auth pages
    if (to.path.startsWith('/auth/')) {
        return
    }

    const { loggedIn } = useUserSession()

    // Redirect to login if not authenticated
    if (loggedIn.value === false && to.query.guest !== '1') {
        return navigateTo('/auth/login')
    }
})

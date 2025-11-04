export const useAuthStore = defineStore('auth', () => {
    const isAuthenticated = useCookie('logged_in', { default: () => false })
    const user = ref<UserResponse | null>(null)

    const fetch = async () => {
        try {
            user.value = await useNuxtApp().$leporid<UserResponse>('/api/users/me')
            isAuthenticated.value = !!user.value
        }
        catch (e: any) {
            if (e.statusCode === 401) {
                user.value = null
                isAuthenticated.value = false
            }
        }
    }

    const lazyFetch = async () => {
        if (!user.value && isAuthenticated.value)
            await fetch()
    }

    const clear = async () => {
        await useNuxtApp().$leporid<UserResponse>('/api/auth/logout', { method: 'POST' })
        user.value = null
        isAuthenticated.value = false
    }

    return {
        isAuthenticated,
        user,
        fetch,
        lazyFetch,
        clear,
    }
})

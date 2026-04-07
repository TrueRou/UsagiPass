interface ApiFetchOptions {
    showErrorToast?: boolean
    showSuccessToast?: boolean
    successMessage?: string
}

interface ApiResponse<T = unknown> {
    code?: number
    message?: string
    data?: T
}

export default defineNuxtPlugin((nuxtApp) => {
    let pendingRequestCount = 0

    const startGlobalLoading = () => {
        if (!import.meta.client)
            return

        pendingRequestCount += 1
        if (pendingRequestCount === 1) {
            const loadingIndicator = useLoadingIndicator()
            loadingIndicator.start()
        }
    }

    const stopGlobalLoading = () => {
        if (!import.meta.client)
            return

        pendingRequestCount = Math.max(0, pendingRequestCount - 1)
        if (pendingRequestCount === 0) {
            const loadingIndicator = useLoadingIndicator()
            loadingIndicator.finish()
        }
    }

    const shouldShowErrorToast = (options?: ApiFetchOptions, method?: string) => {
        if (options?.showErrorToast !== undefined)
            return options.showErrorToast

        return (method || 'GET').toUpperCase() !== 'GET'
    }

    const addToast = (type: 'success' | 'error', message: string) => {
        if (!import.meta.client)
            return

        const { addNotification } = useNotificationsStore()
        addNotification({ type, message })
    }

    const showErrorToast = (message: string, options?: ApiFetchOptions, method?: string) => {
        if (shouldShowErrorToast(options, method)) {
            addToast('error', message)
        }
    }

    const showSuccessToast = (message: string, options?: ApiFetchOptions) => {
        if (options?.showSuccessToast === true) {
            addToast('success', message)
        }
    }

    const handleUnauthorized = async (message?: string) => {
        if (import.meta.server) {
            // hey bro, handle this in composable, throwing and error here will wrap it with FetchError
            console.warn(`[auth-ssr] Unauthorized access detected on server side. throwing: ${message}`)
            throw createError({ statusCode: 401, message: '登录状态过期，请重新登录。' })
        }

        await useUserSession().clear()

        const route = useRoute()
        if (route.path === '/auth/login') {
            return
        }

        addToast('error', message || '登录状态过期，请重新登录。')
        const redirect = encodeURIComponent(route.fullPath || '/')
        await nuxtApp.runWithContext(() => navigateTo(`/auth/login?redirect=${redirect}`))
    }

    const leporid = $fetch.create({
        onRequest(context) {
            if (import.meta.server) {
                const reqHeaders = useRequestHeaders(['cookie'])
                const cookie = reqHeaders.cookie || ''
                const headers = new Headers(context.options.headers as HeadersInit | undefined)
                headers.set('cookie', cookie)
                context.options.headers = headers
            }

            startGlobalLoading()
        },
        onRequestError(context) {
            stopGlobalLoading()

            const options = context.options as ApiFetchOptions
            const message = context.error?.message || '请求失败，请稍后重试。'
            showErrorToast(message, options, context.options.method?.toString())
        },
        async onResponse(context) {
            stopGlobalLoading()

            const options = context.options as ApiFetchOptions
            const rawData = context.response._data as ApiResponse | undefined

            if (!rawData || rawData.code === undefined) {
                return
            }

            if (rawData.code === 200) {
                showSuccessToast(options.successMessage || rawData.message || '操作成功', options)
                if (rawData.data !== undefined) {
                    context.response._data = rawData.data
                }
                return
            }

            const message = rawData.message || context.response.statusText || '请求失败，请稍后重试。'
            if (rawData.code === 401) {
                await handleUnauthorized(message)
                return
            }

            showErrorToast(message, options, context.options.method?.toString())
            throw createError({
                statusCode: context.response.status || 400,
                data: rawData,
                message,
            })
        },
    })

    return {
        provide: {
            leporid,
        },
    }
})

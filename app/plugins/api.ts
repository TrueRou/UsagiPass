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

    const showErrorToast = (message: string, options?: ApiFetchOptions) => {
        if (!import.meta.client)
            return

        if (options?.showErrorToast === true) {
            const { addNotification } = useNotificationsStore()
            addNotification({ type: 'error', message })
        }
    }

    const showSuccessToast = (message: string, options?: ApiFetchOptions) => {
        if (!import.meta.client)
            return

        if (options?.showSuccessToast === true) {
            const { addNotification } = useNotificationsStore()
            addNotification({ type: 'success', message })
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

        showErrorToast(message || '登录状态过期，请重新登录。', { showErrorToast: true })
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
            showErrorToast(context.error?.message || '请求发送失败，请稍后重试。', context.options as ApiFetchOptions)
        },
        async onResponse(context) {
            stopGlobalLoading()
            const rawData = context.response._data as ApiResponse

            if (rawData.data !== undefined && rawData.code === 200) {
                showSuccessToast(rawData.message || '请求成功', context.options as ApiFetchOptions)
                context.response._data = rawData.data // unwrap data
            }

            const message = rawData.message || context.response.statusText
            if (rawData !== undefined && rawData.code === 401) {
                await handleUnauthorized(message)
            }

            if (rawData !== undefined && rawData.code !== 200) {
                showErrorToast(message, context.options as ApiFetchOptions)
                throw createError({
                    statusCode: context.response.status || 400,
                    data: rawData,
                    message,
                })
            }
        },
    })

    return {
        provide: {
            leporid,
        },
    }
})

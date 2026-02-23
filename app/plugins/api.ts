export default defineNuxtPlugin((_nuxtApp) => {
    const leporid = $fetch.create({
        onRequest(context) {
            if (import.meta.server) {
                const reqHeaders = useRequestHeaders(['cookie'])
                context.options.headers.set('cookie', reqHeaders.cookie || '')
            }

            if (import.meta.client) {
                const loadingIndicator = useLoadingIndicator()
                loadingIndicator.start()
            }
        },
        onRequestError() {
            if (import.meta.client) {
                const loadingIndicator = useLoadingIndicator()
                loadingIndicator.finish()
            }
        },
        onResponse(context) {
            const rawData = context.response._data

            if (rawData.code === 200 && rawData.data !== undefined) {
                context.response._data = rawData.data // unwrap data
            }

            if (import.meta.client) {
                const loadingIndicator = useLoadingIndicator()
                loadingIndicator.finish()

                const { addNotification } = useNotificationsStore()
                if (rawData.code === 200 && (context.options as any).showSuccessToast) {
                    addNotification({
                        type: 'success',
                        message: (context.options as any).successMessage || '操作成功',
                    })
                }

                if (rawData.code !== undefined && rawData.code !== 200) {
                    const message = rawData.message || context.response.statusText
                    addNotification({
                        type: 'error',
                        message,
                    })
                    throw new Error(message)
                }
            }
        },
    })

    return {
        provide: {
            leporid,
        },
    }
})

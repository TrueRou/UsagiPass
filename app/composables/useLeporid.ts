import type { UseFetchOptions } from 'nuxt/app'

interface UseApiOptions {
    showErrorToast?: boolean
    showSuccessToast?: boolean
    successMessage?: string
}

export async function useLeporid<T = any>(url: string, options: UseFetchOptions<T> & UseApiOptions = {}) {
    const asyncData = await useFetch<T>(url, {
        ...(options as any),
        $fetch: useNuxtApp().$leporid,
    })

    // 服务器端如果发生错误，需要 Nuxt 处理并显示错误页面
    if (import.meta.server && asyncData.error.value) {
        const error = asyncData.error.value
        throw createError({
            statusCode: error.statusCode || error.status || 500,
            statusMessage: error.statusMessage,
            message: error.message,
            data: {
                to: '/auth/login',
                hint: '重新登录',
                clear: true,
            },
        })
    }

    return asyncData
}

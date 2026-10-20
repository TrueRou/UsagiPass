import type { AnyServerRouteMethod, KeysOf, UseFetchOptions } from 'nuxt/app'

interface UseApiOptions {
    showErrorToast?: boolean
    showSuccessToast?: boolean
    successMessage?: string
}

// Nuxt 4.6 起 UseFetchOptions 的 method 泛型默认收窄为 'get'，这里显式放开为任意方法
type LeporidaeFetchOptions<T> = UseFetchOptions<T, T, KeysOf<T>, undefined, string, AnyServerRouteMethod>

export async function useLeporidae<T = any>(url: string, options: LeporidaeFetchOptions<T> & UseApiOptions = {}) {
    const asyncData = await useFetch<T>(url, {
        ...(options as any),
        $fetch: useNuxtApp().$leporidae,
    })

    // 服务器端如果发生错误，需要 Nuxt 处理并显示错误页面
    if (import.meta.server && asyncData.error.value) {
        const error = asyncData.error.value
        const statusCode = error.statusCode || error.status || 500
        throw createError({
            statusCode,
            statusMessage: error.statusMessage,
            message: error.message,
            data: statusCode === 401
                ? {
                        to: '/auth/login',
                        hint: '重新登录',
                        clear: true,
                    }
                : error.data,
        })
    }

    return asyncData
}

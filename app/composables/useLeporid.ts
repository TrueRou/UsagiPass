import type { UseFetchOptions } from 'nuxt/app'

interface UseApiOptions {
    showErrorToast?: boolean
    showSuccessToast?: boolean
    successMessage?: string
}

export function useLeporid<T = any>(url: string, options: UseFetchOptions<T> & UseApiOptions = {}) {
    return useFetch<T>(url, {
        ...(options as any),
        $fetch: useNuxtApp().$leporid,
    })
}

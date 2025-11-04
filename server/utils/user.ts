import type { H3Event } from 'h3'

export async function useUser(event: H3Event): Promise<UserResponse> {
    const cookieName = useRuntimeConfig().leporid.cookieName
    const leporidCookie = getCookie(event, cookieName)

    try {
        const response = await $fetch<{ data: UserResponse }>('/api/users/me', {
            headers: {
                Cookie: `${cookieName}=${leporidCookie}`,
            },
        })
        return response.data
    }
    catch (e: any) {
        if (e.statusCode === 401) {
            deleteCookie(event, cookieName)
            deleteCookie(event, 'logged_in')
            throw createError({ statusCode: 401, message: '会话不存在或已被撤销' })
        }
        throw e
    }
}

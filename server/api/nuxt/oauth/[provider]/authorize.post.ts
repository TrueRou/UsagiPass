import { joinURL } from 'ufo'

export default defineEventHandler(async (event) => {
    const session = await requireUserSession(event)
    const provider = getRouterParam(event, 'provider')
    if (!isProberOAuthServer(provider)) {
        return {
            code: 400,
            message: '该查分器不支持授权绑定',
            data: null,
        }
    }

    const response = await $fetch<{
        code: number
        message: string
        data?: { authorize_url: string, state: string, expires_in: number }
    }>(`/api/maimai/oauth/${provider}/authorize`, {
        method: 'POST',
        ignoreResponseError: true,
        body: {
            redirect_uri: joinURL(useRuntimeConfig().public.URL, '/oauth/callback', provider),
            // 回调时据此确认授权归属当前登录用户
            context: { app: 'usagipass', user_id: session.user.id },
        },
    })

    if (response.code !== 200 || !response.data) {
        return {
            code: 400,
            message: response.message || '发起授权失败，请稍后再试',
            data: null,
        }
    }

    return {
        code: 200,
        message: '请求成功',
        data: response.data,
    }
})

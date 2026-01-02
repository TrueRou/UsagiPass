export default defineEventHandler(async (event) => {
    const { username, password, strategy }: UserAuthRequest = await readBody(event)

    try {
        const loginForm = new FormData()
        loginForm.append('grant_type', 'password')
        loginForm.append('username', username)
        loginForm.append('password', password)
        loginForm.append('strategy', strategy.toString())

        const tokenResponse = await $fetch<UserAuthResponse>(`/api/auth/token`, {
            method: 'POST',
            body: loginForm,
        })

        const userResponse = await $fetch<{ data: UserResponse }>(`/api/users/me`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${tokenResponse.access_token}`,
            },
        })

        await setUserSession(event, {
            user: {
                id: userResponse.data.id,
                username: userResponse.data.username,
                email: userResponse.data.email,
                permissions: userResponse.data.permissions,
            },
            secure: {
                accessToken: tokenResponse.access_token,
                refreshToken: tokenResponse.refresh_token,
                expiresAt: Date.now() + (tokenResponse.expires_in * 1000),
            },
        })

        return {
            code: 200,
            message: '请求成功',
            data: {},
        }
    }
    catch (error: any) {
        return {
            code: error.statusCode || 500,
            message: error.data.message ?? '未知错误',
            data: null,
        }
    }
})

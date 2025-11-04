export function useWechatCrawl() {
    const triggerCrawl = async () => {
        const { addNotification } = useNotificationsStore()

        // // 检查 UA 确保是在微信内打开
        // if (!navigator.userAgent.toLowerCase().includes('micromessenger')) {
        //     addNotification({ type: 'error', message: '请在微信内打开此页面以使用该功能' })
        //     return
        // }

        // // 检查代理是否可用（使用$fetch以绕过Leporid相关中间件）
        // await $fetch('http://tgk-wcaime.wahlap.com/test', {
        //     method: 'GET',
        //     onResponseError() {
        //         addNotification({ type: 'error', message: '代理配置有误，请更新订阅后重试' })
        //     },
        // })

        // 发起 OAuth 请求，进行页面重定向
        await $fetch('https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx', {
            method: 'GET',
            onResponse({ response }) {
                addNotification({ type: 'info', message: 'w3...' })
                const redirectLocation = response.headers.get('location')
                if (redirectLocation && redirectLocation.includes('redirect_uri=https')) {
                    window.location.href = redirectLocation.replace('redirect_uri=https', 'redirect_uri=http')
                }
                addNotification({ type: 'info', message: '正在跳转至微信服务号进行认证...' })
            },
            onResponseError() {
                addNotification({ type: 'error', message: '无法发起微信服务号OAuth认证' })
            },
        })
    }
    return { triggerCrawl }
}

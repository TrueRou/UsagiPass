export function useWechatCrawl() {
    const triggerCrawl = async (context: { date: string, time: string, maid: string }) => {
        const { addNotification } = useNotificationsStore()

        // 检查 UA 确保是在微信内打开
        if (!navigator.userAgent.toLowerCase().includes('micromessenger')) {
            addNotification({ type: 'error', message: '请在微信内打开此页面以使用该功能' })
            return
        }

        // 检查代理是否可用（使用$fetch以绕过Leporid相关中间件）
        await $fetch('http://tgk-wcaime.wahlap.com/test', {
            method: 'GET',
            onResponseError() {
                addNotification({ type: 'error', message: '代理配置有误，请更新订阅后重试' })
            },
        })

        // 发起 OAuth 请求，进行页面重定向
        const redirectUrl = await useNuxtApp().$leporid<{ url: string }>('/api/otoge/maimai/wechat_oauth', {
            method: 'GET',
            onResponseError() {
                addNotification({ type: 'error', message: '无法发起微信服务号OAuth认证' })
            },
        })

        // 储存当前上下文然后跳转
        localStorage.setItem('context', JSON.stringify(context))
        window.location.href = redirectUrl.url
    }
    return { triggerCrawl }
}

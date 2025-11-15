export function useWechatCrawl() {
    const triggerCrawl = async (context: { date: string, time: string, maid: string }) => {
        const { addNotification, removeNotification } = useNotificationsStore()

        // 检查 UA 确保是在微信内打开
        if (!navigator.userAgent.toLowerCase().includes('micromessenger')) {
            addNotification({ type: 'error', message: '请在微信内打开此页面以使用该功能' })
            return
        }

        const alert = addNotification({ type: 'info', message: '正在发起微信服务号 OAuth 认证' })

        try {
            // 发起 OAuth 请求
            const redirectUrl = await useNuxtApp().$leporid<{ url: string }>('/api/otoge/maimai/wechat_oauth', { method: 'GET' })

            // 储存当前上下文然后跳转
            removeNotification(alert)
            localStorage.setItem('context', JSON.stringify(context))
            window.location.href = redirectUrl.url
        }
        catch {
            removeNotification(alert)
            addNotification({ type: 'error', message: '无法发起微信服务号 OAuth 认证' })
        }
    }
    return { triggerCrawl }
}

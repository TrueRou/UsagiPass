export function useWechatCrawl() {
    const triggerCrawl = async (context: { date: string, time: string, maid: string }) => {
        const { addNotification } = useNotificationsStore()
        const { loggedIn } = useUserSession()

        if (!loggedIn.value) {
            addNotification({ type: 'error', message: '请先登录以使用该功能' })
            return
        }

        // 检查 UA 确保是在微信内打开
        if (!navigator.userAgent.toLowerCase().includes('micromessenger')) {
            addNotification({ type: 'error', message: '请在微信内打开此页面以使用该功能' })
            return
        }

        try {
            // 发起 OAuth 请求
            const redirectUrl = await useNuxtApp().$leporid<{ url: string }>('/api/otoge/maimai/wechat_oauth', { method: 'GET' })

            // 储存当前上下文然后跳转
            localStorage.setItem('context', JSON.stringify(context))
            window.location.href = redirectUrl.url
        }
        catch {
            addNotification({ type: 'error', message: '无法发起微信服务号 OAuth 认证' })
        }
    }
    return { triggerCrawl }
}

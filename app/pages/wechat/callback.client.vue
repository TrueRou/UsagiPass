<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })

const route = useRoute()
const { addNotification, removeNotification } = useNotificationsStore()

async function handleCallback() {
    // 恢复上下文并跳转回首页
    const context: { date: string, time: string, maid: string } = JSON.parse(localStorage.getItem('context') || '{}')
    localStorage.removeItem('context')
    await navigateTo({ path: '/', query: context })

    const notificationId = addNotification({
        type: 'info',
        message: '查分器更新请求处理中...',
        duration: 60 * 1000,
    })

    await useLeporid('/api/nuxt/wechat/callback', {
        method: 'POST',
        body: {
            code: route.query.code,
            r: route.query.r,
            t: route.query.t,
            state: route.query.state,
        },
        showSuccessToast: true,
        successMessage: '查分器更新成功',
    })

    // 等待一秒以确保用户看到通知
    setTimeout(() => removeNotification(notificationId), 1000)
}

onMounted(() => handleCallback())
</script>

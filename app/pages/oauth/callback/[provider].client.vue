<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })
useHead({
    title: '查分器授权 - UsagiPass',
    // 回调地址携带一次性授权码，避免经 Referer 泄露
    meta: [{ name: 'referrer', content: 'no-referrer' }],
})

const route = useRoute()
const router = useRouter()

const errorMessage = ref('')

async function handleCallback() {
    const provider = String(route.params.provider ?? '')
    const code = typeof route.query.code === 'string' ? route.query.code : ''
    const state = typeof route.query.state === 'string' ? route.query.state : ''
    const upstreamError = typeof route.query.error === 'string' ? route.query.error : ''
    // 立即从地址栏移除授权码，避免刷新时重复提交
    await router.replace({ path: route.path, query: {} })

    if (!state || !consumeProberOAuthState(state, provider)) {
        errorMessage.value = '授权请求已过期或不是由本设备发起，请返回偏好设置重新授权。'
        return
    }
    if (upstreamError || !code) {
        errorMessage.value = upstreamError === 'access_denied' ? '你已取消授权。' : '授权失败，请返回偏好设置重新授权。'
        return
    }

    try {
        await useNuxtApp().$leporidae(`/api/nuxt/oauth/${provider}/callback`, {
            method: 'POST',
            body: { code, state },
            showErrorToast: false,
            showSuccessToast: true,
        } as any)
    }
    catch (e: any) {
        errorMessage.value = e?.data?.message || e?.message || '授权失败，请返回偏好设置重新授权。'
        return
    }
    await navigateTo('/preference')
}

onMounted(() => handleCallback())
</script>

<template>
    <div class="min-h-screen bg-base-200 flex items-center justify-center px-4">
        <div class="card bg-base-100 w-full max-w-md">
            <div class="card-body space-y-4">
                <h1 class="card-title">
                    绑定查分器账号
                </h1>
                <template v-if="errorMessage">
                    <div class="alert alert-warning text-sm">
                        <span>{{ errorMessage }}</span>
                    </div>
                    <NuxtLink to="/preference" class="btn btn-primary">
                        返回偏好设置
                    </NuxtLink>
                </template>
                <div v-else class="flex items-center gap-3 text-sm text-base-content/70">
                    <span class="loading loading-spinner loading-sm" />
                    <span>正在完成授权…</span>
                </div>
            </div>
        </div>
    </div>
</template>

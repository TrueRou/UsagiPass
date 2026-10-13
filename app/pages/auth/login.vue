<script setup lang="ts">
useHead({
    title: '登录 - UsagiPass',
})

const { loggedIn, clear } = useUserSession()
const route = useRoute()
const guestCookie = useCookie<boolean>('guest', { maxAge: 60 * 60 * 24 * 365 })
guestCookie.value = false

if (route.query.clear === '1' || route.query.clear === 'true') {
    await clear()

    const nextQuery = { ...route.query }
    delete nextQuery.clear

    await navigateTo({
        path: route.path,
        query: nextQuery,
    }, { replace: true })
}

// 登录后的跳转目标：仅允许站内路径
const redirectTarget = computed(() => {
    const r = route.query.redirect as string
    if (r && r.startsWith('/') && !r.startsWith('//') && !r.startsWith('/auth/'))
        return r
    return '/'
})

const loginError = computed(() => (typeof route.query.error === 'string' ? route.query.error : ''))

if (loggedIn.value)
    await navigateTo(redirectTarget.value, { replace: true })

function oauthURL(prompt?: 'create') {
    const query = new URLSearchParams({ redirect: redirectTarget.value })
    if (prompt)
        query.set('prompt', prompt)
    return `/api/nuxt/auth/leporidae?${query}`
}

async function handleLogin(prompt?: 'create') {
    await navigateTo(oauthURL(prompt), { external: true })
}

async function handleGuestMode() {
    // 游客模式意味着“不使用账号”，因此必须清掉已有会话，
    // 否则会出现已登录却读到游客默认值的情况
    await clear()
    guestCookie.value = true
    await navigateTo('/', { external: true })
}
</script>

<template>
    <div>
        <BannerAccountSystem />

        <div class="max-w-md mx-auto px-4 pt-16">
            <h1 class="text-3xl font-bold text-center mb-4">
                登录
            </h1>
            <p class="text-center text-sm text-base-content/70 mb-8">
                使用 UsagiLab 通行证（原兔卡账号）登录，登录与密码管理将在 UsagiLab 官网完成。
            </p>

            <div v-if="loginError" role="alert" class="alert alert-error alert-soft mb-6 text-sm">
                {{ loginError }}
            </div>

            <button type="button" class="btn btn-primary w-full" @click="handleLogin()">
                使用 UsagiLab 账号登录
            </button>

            <button type="button" class="btn btn-outline w-full mt-2" @click="handleGuestMode">
                <img src="../../assets/icons/misc/offline.png" alt="guest" class="inline h-6">
                要使用游客模式吗
            </button>

            <hr class="my-8">

            <p class="text-center text-sm">
                没有账户？
                <a :href="oauthURL('create')" class="link link-primary" @click.prevent="handleLogin('create')">
                    注册
                </a>
            </p>
        </div>
    </div>
</template>

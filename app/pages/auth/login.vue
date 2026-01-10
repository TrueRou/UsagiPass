<script setup lang="ts">
import { z } from 'zod'

useHead({
    title: '登录 - UsagiPass',
})

const { loggedIn, fetch: fetchUser, user } = useUserSession()
const guestCookie = useCookie<boolean>('guest', { maxAge: 60 * 60 * 24 * 365 })
guestCookie.value = false

const shouldCompleteProfile = computed(() => (user.value?.email?.trim()?.length ?? 0) === 0)

const strategyOptions: Array<{ value: AuthStrategy, name: string, desc: string, passwordLabel: string, usernameLabel?: string }> = [
    { value: AuthStrategy.LOCAL, name: 'UsagiLab 通行证', desc: '使用 UsagiLab 通行证（原兔卡账号）登录', passwordLabel: '密码', usernameLabel: '用户名' },
    { value: AuthStrategy.DIVING_FISH, name: '水鱼 · DIVING-FISH', desc: '使用此前绑定的水鱼查分器账号密码登录', passwordLabel: '密码', usernameLabel: '用户名' },
    { value: AuthStrategy.LXNS, name: '落雪 · LXNS', desc: '使用此前绑定的落雪咖啡屋个人 API 密钥登录', passwordLabel: '个人密钥', usernameLabel: undefined },
]

// Redirect if already logged in
watchEffect(() => {
    if (!loggedIn.value)
        return

    navigateTo(shouldCompleteProfile.value ? '/auth/reset' : '/')
})

// Zod schema for validation
const loginSchema = z.object({
    username: z.string().min(1, '用户名不能为空'),
    password: z.string().min(1, '密码不能为空'),
    refresh_token: z.string().optional(),
    strategy: z.number(),
})

interface LoginForm {
    username: string
    password: string
    refresh_token?: string
    strategy: AuthStrategy
}

const form = reactive<LoginForm>({
    username: '',
    password: '',
    strategy: AuthStrategy.LOCAL,
})

const { validate, ve } = useFormValidation(loginSchema, form)

async function handleLogin() {
    if (!validate())
        return

    await useNuxtApp().$leporid('/api/nuxt/auth/login', {
        method: 'POST',
        body: {
            username: form.username,
            password: form.password,
            strategy: form.strategy,
        },
        showSuccessToast: true,
        successMessage: '登录成功！',
    })

    await fetchUser()
    await navigateTo(shouldCompleteProfile.value ? '/auth/profile-update' : '/')
}

async function handleGuestMode() {
    guestCookie.value = true
    await navigateTo('/')
}

useHead({
    title: '登录',
})
</script>

<template>
    <div>
        <BannerAccountSystem />

        <div class="max-w-md mx-auto px-4 pt-16">
            <h1 class="text-3xl font-bold text-center mb-8">
                登录
            </h1>

            <form class="space-y-6" @submit.prevent="handleLogin">
                <div v-if="strategyOptions[form.strategy]?.usernameLabel">
                    <label class="block text-sm font-medium mb-2">{{ strategyOptions[form.strategy]?.usernameLabel }}</label>
                    <input
                        v-model="form.username" type="text" :placeholder="`请输入${strategyOptions[form.strategy]?.usernameLabel}`"
                        class="input input-bordered w-full" :class="{ 'input-error': ve('username') }"
                    >
                    <p v-if="ve('username')" class="text-error text-sm mt-1">
                        {{ ve('username') }}
                    </p>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">{{ strategyOptions[form.strategy]?.passwordLabel }}</label>
                    <input
                        v-model="form.password" type="password" :placeholder="`请输入${strategyOptions[form.strategy]?.passwordLabel}`"
                        class="input input-bordered w-full" :class="{ 'input-error': ve('password') }"
                    >
                    <p v-if="ve('password')" class="text-error text-sm mt-1">
                        {{ ve('password') }}
                    </p>
                </div>

                <div>
                    <p class="block text-sm font-medium mb-3">
                        登录方式
                    </p>
                    <div class="space-y-3">
                        <label
                            v-for="option in strategyOptions" :key="option.value"
                            class="flex items-start gap-3 rounded-box border border-base-300 px-3 py-2"
                        >
                            <input
                                v-model="form.strategy" type="radio" class="radio radio-primary mt-1"
                                :value="option.value"
                            >
                            <div>
                                <p class="font-medium text-sm">
                                    {{ option.name }}
                                </p>
                                <p class="text-xs text-base-content/70">
                                    {{ option.desc }}
                                </p>
                            </div>
                        </label>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary w-full">
                    登录
                </button>
            </form>

            <button type="button" class="btn btn-outline w-full mt-2" @click="handleGuestMode">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                要使用游客模式吗
            </button>

            <hr class="my-8">

            <p class="text-center text-sm">
                没有账户？
                <NuxtLink to="/auth/register" class="link link-primary">
                    注册
                </NuxtLink>
            </p>
        </div>
    </div>
</template>

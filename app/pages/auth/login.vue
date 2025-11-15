<script setup lang="ts">
import { z } from 'zod'

useHead({
    title: '登录 - UsagiPass',
})

const { loggedIn, fetch: fetchUser, user } = useUserSession()

const shouldCompleteProfile = computed(() => (user.value?.email?.trim()?.length ?? 0) === 0)

type LoginStrategy = 'LOCAL' | 'DIVING_FISH' | 'LXNS'

const strategyOptions: Array<{ value: LoginStrategy, name: string, desc: string }> = [
    { value: 'LOCAL', name: 'UsagiLab 通行证', desc: '使用 UsagiLab 统一认证登录' },
    { value: 'DIVING_FISH', name: '水鱼 · DIVING_FISH', desc: '使用绑定的 DivingFish 账号密码登录' },
    { value: 'LXNS', name: '落雪 · LXNS', desc: '使用绑定的 LXNS 个人 API 密钥登录' },
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
    strategy: z.enum(['LOCAL', 'DIVING_FISH', 'LXNS']).default('LOCAL'),
})

interface LoginForm {
    username: string
    password: string
    refresh_token?: string
    strategy: LoginStrategy
}

const form = reactive<LoginForm>({
    username: '',
    password: '',
    strategy: 'LOCAL' as LoginStrategy,
})

const { validate, ve } = useFormValidation(loginSchema, form)

async function handleLogin() {
    if (!validate())
        return

    const body: Record<string, string> = {
        username: form.username,
        password: form.password,
    }

    if (form.strategy !== 'LOCAL')
        body.strategy = form.strategy

    await useNuxtApp().$leporid('/api/nuxt/auth/login', {
        method: 'POST',
        body,
        showSuccessToast: true,
        successMessage: '登录成功！',
    })

    await fetchUser()
    await navigateTo(shouldCompleteProfile.value ? '/auth/profile-update' : '/')
}

useHead({
    title: '登录',
})
</script>

<template>
    <div class="max-w-md mx-auto px-4 pt-16">
        <h1 class="text-3xl font-bold text-center mb-8">
            登录
        </h1>

        <form class="space-y-6" @submit.prevent="handleLogin">
            <div>
                <label class="block text-sm font-medium mb-2">用户名</label>
                <input
                    v-model="form.username" type="text" placeholder="请输入用户名"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('username') }"
                >
                <p v-if="ve('username')" class="text-error text-sm mt-1">
                    {{ ve('username') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">密码 / 个人密钥</label>
                <input
                    v-model="form.password" type="password" placeholder="请输入密码"
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

        <hr class="my-8">

        <p class="text-center text-sm">
            没有账户？
            <NuxtLink to="/auth/register" class="link link-primary">
                注册
            </NuxtLink>
        </p>
    </div>
</template>

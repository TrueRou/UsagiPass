<script setup lang="ts">
import { z } from 'zod'

const { t } = useI18n()
const { loggedIn, fetch: fetchUser } = useUserSession()

// Redirect if already logged in
watchEffect(() => {
    if (loggedIn.value) {
        navigateTo('/')
    }
})

// Extended register form with confirmPassword
interface RegisterForm extends UserRegisterRequest {
    confirmPassword: string
}

// Zod schema for validation
const registerSchema = z.object({
    username: z.string().min(3, t('username-min-length')),
    email: z.email(),
    password: z.string().min(6, t('password-min-length')),
    confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
    message: t('password-mismatch'),
    path: ['confirmPassword'],
})

const form = reactive<RegisterForm>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
})

const { validate, ve } = useFormValidation(registerSchema, form)

async function handleRegister() {
    if (!validate())
        return

    const requestData: UserRegisterRequest = {
        username: form.username,
        password: form.password,
        email: form.email,
    }

    await useNuxtApp().$leporid('/api/auth/register', {
        method: 'POST',
        body: requestData,
        showSuccessToast: true,
        successMessage: t('register-success'),
    })

    await useNuxtApp().$leporid('/api/nuxt/auth/login', {
        method: 'POST',
        body: form,
        showSuccessToast: true,
        successMessage: t('login-success'),
    })

    await fetchUser()
    await navigateTo('/')
}

useHead({
    title: t('register'),
})
</script>

<template>
    <div class="max-w-md mx-auto pt-16">
        <h1 class="text-3xl font-bold text-center mb-8">
            {{ t('register') }}
        </h1>

        <form class="space-y-6" @submit.prevent="handleRegister">
            <div>
                <label class="block text-sm font-medium mb-2">{{ t('username') }}</label>
                <input
                    v-model="form.username" type="text" :placeholder="t('username-placeholder')"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('username') }"
                >
                <p v-if="ve('username')" class="text-error text-sm mt-1">
                    {{ ve('username') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">{{ t('email') }}</label>
                <input
                    v-model="form.email" type="email" :placeholder="t('email-placeholder')"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('email') }"
                >
                <p v-if="ve('email')" class="text-error text-sm mt-1">
                    {{ ve('email') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">{{ t('password') }}</label>
                <input
                    v-model="form.password" type="password" :placeholder="t('password-placeholder')"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('password') }"
                >
                <p v-if="ve('password')" class="text-error text-sm mt-1">
                    {{ ve('password') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">{{ t('confirm-password') }}</label>
                <input
                    v-model="form.confirmPassword" type="password" :placeholder="t('confirm-password-placeholder')"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('confirmPassword') }"
                >
                <p v-if="ve('confirmPassword')" class="text-error text-sm mt-1">
                    {{ ve('confirmPassword') }}
                </p>
            </div>

            <button type="submit" class="btn btn-primary w-full">
                {{ t('register') }}
            </button>
        </form>

        <hr class="my-8">

        <p class="text-center text-sm">
            {{ t('have-account') }}
            <NuxtLink to="/auth/login" class="link link-primary">
                {{ t('login') }}
            </NuxtLink>
        </p>
    </div>
</template>

<i18n lang="yaml">
en-GB:
    register: Register
    username: Username
    username-placeholder: Enter your username
    username-min-length: Username must be at least 3 characters
    email: Email
    email-placeholder: Enter your email
    password: Password
    password-placeholder: Enter your password
    password-min-length: Password must be at least 6 characters
    confirm-password: Confirm password
    confirm-password-placeholder: Re-enter your password
    password-mismatch: Passwords do not match
    register-success: Registration successful
    have-account: Already have an account?
    login: Log in
zh-CN:
    register: 注册
    username: 用户名
    username-placeholder: 输入用户名
    username-min-length: 用户名至少需要 3 个字符
    email: 邮箱
    email-placeholder: 输入邮箱
    password: 密码
    password-placeholder: 输入密码
    password-min-length: 密码至少需要 6 个字符
    confirm-password: 确认密码
    confirm-password-placeholder: 再次输入密码
    password-mismatch: 两次输入的密码不一致
    register-success: 注册成功
    have-account: 已有账号？
    login: 登录
</i18n>

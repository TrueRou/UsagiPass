<script setup lang="ts">
import { z } from 'zod'

useHead({
    title: '注册 - UsagiPass',
})

const { loggedIn, fetch: fetchUser } = useUserSession()

// Redirect if already logged in
watchEffect(() => {
    if (loggedIn.value) {
        navigateTo('/')
    }
})

// Extended register form with confirmPassword
interface RegisterForm extends UserCreateRequest {
    confirmPassword: string
}

// Zod schema for validation
const registerSchema = z.object({
    username: z.string().min(3, '用户名至少需要 3 个字符'),
    email: z.email(),
    password: z.string().min(6, '密码至少需要 6 个字符'),
    confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
    message: '两次输入的密码不一致',
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

    const requestData: UserCreateRequest = {
        username: form.username,
        password: form.password,
        email: form.email,
    }

    await useNuxtApp().$leporid('/api/auth/register', {
        method: 'POST',
        body: requestData,
        showSuccessToast: true,
        successMessage: '注册成功',
    })

    await useNuxtApp().$leporid('/api/nuxt/auth/login', {
        method: 'POST',
        body: form,
        showSuccessToast: true,
        successMessage: '登录成功！',
    })

    await fetchUser()
    await navigateTo('/')
}

useHead({
    title: '注册',
})
</script>

<template>
    <div class="max-w-md mx-auto px-4 pt-16">
        <h1 class="text-3xl font-bold text-center mb-8">
            注册
        </h1>

        <form class="space-y-6" @submit.prevent="handleRegister">
            <div>
                <label class="block text-sm font-medium mb-2">用户名</label>
                <input
                    v-model="form.username" type="text" placeholder="输入用户名"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('username') }"
                >
                <p v-if="ve('username')" class="text-error text-sm mt-1">
                    {{ ve('username') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">邮箱</label>
                <input
                    v-model="form.email" type="email" placeholder="输入邮箱"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('email') }"
                >
                <p v-if="ve('email')" class="text-error text-sm mt-1">
                    {{ ve('email') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">密码</label>
                <input
                    v-model="form.password" type="password" placeholder="输入密码"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('password') }"
                >
                <p v-if="ve('password')" class="text-error text-sm mt-1">
                    {{ ve('password') }}
                </p>
            </div>

            <div>
                <label class="block text-sm font-medium mb-2">确认密码</label>
                <input
                    v-model="form.confirmPassword" type="password" placeholder="再次输入密码"
                    class="input input-bordered w-full" :class="{ 'input-error': ve('confirmPassword') }"
                >
                <p v-if="ve('confirmPassword')" class="text-error text-sm mt-1">
                    {{ ve('confirmPassword') }}
                </p>
            </div>

            <button type="submit" class="btn btn-primary w-full">
                注册
            </button>
        </form>

        <hr class="my-8">

        <p class="text-center text-sm">
            已有账号？
            <NuxtLink to="/auth/login" class="link link-primary">
                登录
            </NuxtLink>
        </p>
    </div>
</template>

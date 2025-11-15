<script setup lang="ts">
import { z } from 'zod'

definePageMeta({ middleware: 'require-login' })
const nuxtApp = useNuxtApp()
const { user, fetch: refreshSession } = useUserSession()

const shouldRedirectHome = computed(() => {
    const email = user.value?.email?.trim() ?? ''
    return email.length > 0
})

watchEffect(() => {
    if (shouldRedirectHome.value)
        navigateTo('/', { replace: true })
})

const form = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
})

const schema = z.object({
    username: z.string().min(3, '用户名至少 3 个字符'),
    email: z.string().email('请输入正确的邮箱地址'),
    password: z.string().min(6, '密码至少 6 个字符'),
    confirmPassword: z.string(),
}).refine(values => values.password === values.confirmPassword, {
    message: '两次输入的密码不一致',
    path: ['confirmPassword'],
})

const { validate, ve, clearErrors } = useFormValidation(schema, form)
const isSubmitting = ref(false)

watch(user, (val) => {
    form.username = val?.username ?? ''
    form.email = ''
    form.password = ''
    form.confirmPassword = ''
    clearErrors()
}, { immediate: true })

async function handleSubmit() {
    if (!validate() || isSubmitting.value)
        return

    isSubmitting.value = true
    try {
        await nuxtApp.$leporid('/api/users/me', {
            method: 'PATCH',
            body: {
                username: form.username,
                email: form.email,
                password: form.password,
            },
            showSuccessToast: true,
            successMessage: '账户信息已更新',
        })
        await refreshSession()
        await navigateTo('/')
    }
    finally {
        isSubmitting.value = false
    }
}

useHead({
    title: '完成账户信息',
})
</script>

<template>
    <div class="max-w-md mx-auto pt-16">
        <div class="space-y-2 text-center">
            <p class="text-xs uppercase tracking-[0.25em] text-warning">
                必须操作
            </p>
            <h1 class="text-2xl font-bold">
                请完善账户信息
            </h1>
            <p class="text-sm text-base-content/70">
                出于安全考虑，请先补充邮箱并重设密码后再继续使用 UsagiPass。
            </p>
        </div>

        <form class="mt-6 space-y-4" @submit.prevent="handleSubmit">
            <div>
                <label class="mb-1 block text-sm font-medium">用户名</label>
                <input
                    v-model="form.username" class="input input-bordered w-full" type="text"
                    :class="{ 'input-error': ve('username') }" placeholder="正在载入用户名"
                    readonly
                >
            </div>

            <div>
                <label class="mb-1 block text-sm font-medium">邮箱</label>
                <input
                    v-model="form.email" class="input input-bordered w-full" type="email"
                    :class="{ 'input-error': ve('email') }" placeholder="请输入有效邮箱"
                >
                <p v-if="ve('email')" class="mt-1 text-xs text-error">
                    {{ ve('email') }}
                </p>
            </div>

            <div>
                <label class="mb-1 block text-sm font-medium">密码</label>
                <input
                    v-model="form.password" class="input input-bordered w-full" type="password"
                    :class="{ 'input-error': ve('password') }" placeholder="输入新密码"
                >
                <p v-if="ve('password')" class="mt-1 text-xs text-error">
                    {{ ve('password') }}
                </p>
            </div>

            <div>
                <label class="mb-1 block text-sm font-medium">确认密码</label>
                <input
                    v-model="form.confirmPassword" class="input input-bordered w-full" type="password"
                    :class="{ 'input-error': ve('confirmPassword') }" placeholder="再次输入新密码"
                >
                <p v-if="ve('confirmPassword')" class="mt-1 text-xs text-error">
                    {{ ve('confirmPassword') }}
                </p>
            </div>

            <p class="flex items-center gap-2 text-xs text-base-content/60">
                <span class="badge badge-info badge-xs" />
                如果您希望进行账户合并等操作，请补全信息后前往设置页面进行。
            </p>

            <button class="btn btn-warning w-full" type="submit" :disabled="isSubmitting">
                <span v-if="isSubmitting" class="loading loading-spinner" />
                <span>立即更新</span>
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { z } from 'zod'

useHead({
    title: '找回密码 - UsagiPass',
})

const forgotSchema = z.object({
    email: z.email('请输入有效的邮箱地址'),
})

const form = reactive<PasswordForgotRequest>({
    email: '',
})

const { validate, ve } = useFormValidation(forgotSchema, form)
const isSubmitting = ref(false)
const sentEmail = ref('')

async function handleSubmit() {
    if (!validate() || isSubmitting.value)
        return

    isSubmitting.value = true
    try {
        await useNuxtApp().$leporidae('/api/auth/password/forgot', {
            method: 'POST',
            body: { email: form.email.trim() },
        })
        sentEmail.value = form.email.trim()
    }
    finally {
        isSubmitting.value = false
    }
}
</script>

<template>
    <div>
        <BannerAccountSystem />

        <div class="max-w-md mx-auto px-4 pt-16">
            <template v-if="!sentEmail">
                <h1 class="text-3xl font-bold text-center mb-3">
                    找回密码
                </h1>
                <p class="text-sm text-base-content/70 text-center mb-8">
                    输入 UsagiLab 通行证绑定的邮箱，我们将发送重置密码链接。
                </p>

                <form class="space-y-6" @submit.prevent="handleSubmit">
                    <div>
                        <label class="block text-sm font-medium mb-2">邮箱</label>
                        <input
                            v-model="form.email" type="email" placeholder="输入注册邮箱" autocomplete="email"
                            class="input input-bordered w-full" :class="{ 'input-error': ve('email') }"
                        >
                        <p v-if="ve('email')" class="text-error text-sm mt-1">
                            {{ ve('email') }}
                        </p>
                    </div>

                    <button type="submit" class="btn btn-primary w-full" :disabled="isSubmitting">
                        <span v-if="isSubmitting" class="loading loading-spinner" />
                        <span>发送重置链接</span>
                    </button>
                </form>

                <p class="text-xs text-base-content/60 mt-4">
                    使用水鱼 / 落雪登录的账号无需重置，请直接使用对应查分器的凭据登录。
                </p>
            </template>

            <div v-else class="text-center">
                <div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-success/15 text-success">
                    <svg xmlns="http://www.w3.org/2000/svg" class="size-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <rect x="3" y="5" width="18" height="14" rx="2" />
                        <path d="m3 7 9 6 9-6" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                </div>
                <h1 class="text-3xl font-bold mb-3">
                    请查收邮件
                </h1>
                <p class="text-sm text-base-content/70">
                    如果
                    <span class="font-medium text-base-content break-all">{{ sentEmail }}</span>
                    已注册，我们已向其发送重置密码链接。
                </p>
                <p class="text-sm text-base-content/70 mt-2">
                    请点击邮件中的按钮设置新密码，完成后返回此处登录。
                </p>
                <p class="text-xs text-base-content/50 mt-2">
                    没有收到？请检查垃圾邮件文件夹，或稍后重试。
                </p>

                <div class="mt-8 space-y-2">
                    <NuxtLink to="/auth/login" class="btn btn-primary w-full">
                        返回登录
                    </NuxtLink>
                    <button type="button" class="btn btn-ghost btn-sm w-full" @click="sentEmail = ''">
                        换个邮箱重新发送
                    </button>
                </div>
            </div>

            <hr class="my-8">

            <p class="text-center text-sm">
                想起密码了？
                <NuxtLink to="/auth/login" class="link link-primary">
                    登录
                </NuxtLink>
            </p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { z } from 'zod'

useHead({
    title: '注册 - UsagiPass',
})

const CODE_LENGTH = 6
const RESEND_SECONDS = 60

const { loggedIn, fetch: fetchUser } = useUserSession()

// Redirect if already logged in
watchEffect(() => {
    if (loggedIn.value) {
        navigateTo('/')
    }
})

// Extended register form with confirmPassword
interface RegisterForm extends Omit<UserCreateRequest, 'code'> {
    confirmPassword: string
}

// Zod schema for validation
const registerSchema = z.object({
    username: z.string().min(3, '用户名至少需要 3 个字符'),
    email: z.email('请输入有效的邮箱地址'),
    password: z.string().min(8, '密码至少需要 8 个字符'),
    confirmPassword: z.string().min(8, '密码至少需要 8 个字符'),
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

// 步骤：info 填写注册信息 → verify 输入邮箱验证码
const step = ref<'info' | 'verify'>('info')
const sentEmail = ref('')
const code = ref('')
const codeError = ref('')
const isSending = ref(false)
const isSubmitting = ref(false)

const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

function startCountdown() {
    countdown.value = RESEND_SECONDS
    clearInterval(timer)
    timer = setInterval(() => {
        countdown.value -= 1
        if (countdown.value <= 0)
            clearInterval(timer)
    }, 1000)
}

onBeforeUnmount(() => clearInterval(timer))

async function requestCode(): Promise<boolean> {
    isSending.value = true
    try {
        const body: RegisterCodeRequest = { email: form.email }
        await useNuxtApp().$leporidae('/api/auth/register/code', {
            method: 'POST',
            body,
        })
        sentEmail.value = form.email
        code.value = ''
        codeError.value = ''
        startCountdown()
        return true
    }
    catch {
        return false
    }
    finally {
        isSending.value = false
    }
}

async function handleNext() {
    if (!validate())
        return

    // 同一邮箱冷却期内直接回到验证码页，不重复发送
    if (sentEmail.value === form.email && countdown.value > 0) {
        step.value = 'verify'
        return
    }

    if (await requestCode())
        step.value = 'verify'
}

async function handleResend() {
    if (countdown.value > 0 || isSending.value)
        return
    if (await requestCode()) {
        useNotificationsStore().addNotification({ type: 'success', message: '验证码已重新发送' })
    }
}

async function handleRegister() {
    if (isSubmitting.value)
        return
    if (code.value.length !== CODE_LENGTH) {
        codeError.value = `请输入 ${CODE_LENGTH} 位验证码`
        return
    }

    codeError.value = ''
    isSubmitting.value = true
    try {
        const requestData: UserCreateRequest = {
            username: form.username,
            password: form.password,
            email: form.email,
            code: code.value,
        }

        await useNuxtApp().$leporidae('/api/auth/register', {
            method: 'POST',
            body: requestData,
            showErrorToast: false,
            showSuccessToast: true,
            successMessage: '注册成功',
        })
    }
    catch (error: any) {
        codeError.value = error?.data?.message || error?.message || '注册失败，请稍后再试'
        code.value = ''
        isSubmitting.value = false
        return
    }

    try {
        await useNuxtApp().$leporidae('/api/nuxt/auth/login', {
            method: 'POST',
            body: {
                username: form.username,
                password: form.password,
            },
            showSuccessToast: true,
            successMessage: '登录成功！',
        })
        await fetchUser()
        await navigateTo('/')
    }
    catch {
        await navigateTo('/auth/login')
    }
    finally {
        isSubmitting.value = false
    }
}

// 验证码输满即自动提交
watch(code, (val) => {
    if (step.value === 'verify' && val.length === CODE_LENGTH)
        handleRegister()
})
</script>

<template>
    <div>
        <BannerAccountSystem />

        <div class="max-w-md mx-auto px-4 pt-16">
            <!-- 步骤指示 -->
            <ul class="steps w-full mb-8">
                <li class="step step-primary">
                    填写信息
                </li>
                <li class="step" :class="{ 'step-primary': step === 'verify' }">
                    验证邮箱
                </li>
            </ul>

            <template v-if="step === 'info'">
                <h1 class="text-3xl font-bold text-center mb-8">
                    注册
                </h1>

                <form class="space-y-6" @submit.prevent="handleNext">
                    <div>
                        <label class="block text-sm font-medium mb-2">用户名</label>
                        <input
                            v-model="form.username" type="text" placeholder="输入用户名" autocomplete="username"
                            class="input input-bordered w-full" :class="{ 'input-error': ve('username') }"
                        >
                        <p v-if="ve('username')" class="text-error text-sm mt-1">
                            {{ ve('username') }}
                        </p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">邮箱</label>
                        <input
                            v-model="form.email" type="email" placeholder="输入邮箱" autocomplete="email"
                            class="input input-bordered w-full" :class="{ 'input-error': ve('email') }"
                        >
                        <p v-if="ve('email')" class="text-error text-sm mt-1">
                            {{ ve('email') }}
                        </p>
                        <p v-else class="text-base-content/60 text-xs mt-1">
                            用于接收验证码与找回密码
                        </p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">密码</label>
                        <input
                            v-model="form.password" type="password" placeholder="输入密码" autocomplete="new-password"
                            class="input input-bordered w-full" :class="{ 'input-error': ve('password') }"
                        >
                        <p v-if="ve('password')" class="text-error text-sm mt-1">
                            {{ ve('password') }}
                        </p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium mb-2">确认密码</label>
                        <input
                            v-model="form.confirmPassword" type="password" placeholder="再次输入密码" autocomplete="new-password"
                            class="input input-bordered w-full" :class="{ 'input-error': ve('confirmPassword') }"
                        >
                        <p v-if="ve('confirmPassword')" class="text-error text-sm mt-1">
                            {{ ve('confirmPassword') }}
                        </p>
                    </div>

                    <button type="submit" class="btn btn-primary w-full" :disabled="isSending">
                        <span v-if="isSending" class="loading loading-spinner" />
                        <span>下一步：验证邮箱</span>
                    </button>
                </form>
            </template>

            <template v-else>
                <div class="text-center">
                    <div class="mx-auto mb-4 flex size-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" class="size-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                            <rect x="3" y="5" width="18" height="14" rx="2" />
                            <path d="m3 7 9 6 9-6" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                    </div>
                    <h1 class="text-3xl font-bold mb-3">
                        验证邮箱
                    </h1>
                    <p class="text-sm text-base-content/70">
                        验证码已发送至
                        <span class="font-medium text-base-content break-all">{{ sentEmail }}</span>
                        <br>
                        请输入邮件中的 {{ CODE_LENGTH }} 位验证码完成注册
                    </p>
                </div>

                <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
                    <div>
                        <AuthCodeInput
                            v-model="code" :length="CODE_LENGTH" :invalid="!!codeError"
                            :disabled="isSubmitting" autofocus
                        />
                        <p v-if="codeError" class="text-error text-sm mt-2 text-center">
                            {{ codeError }}
                        </p>
                    </div>

                    <button type="submit" class="btn btn-primary w-full" :disabled="isSubmitting">
                        <span v-if="isSubmitting" class="loading loading-spinner" />
                        <span>完成注册</span>
                    </button>

                    <div class="text-center text-sm">
                        <span class="text-base-content/70">没有收到邮件？</span>
                        <span v-if="countdown > 0" class="text-base-content/50 tabular-nums">
                            {{ countdown }} 秒后可重新发送
                        </span>
                        <button
                            v-else type="button" class="link link-primary" :disabled="isSending"
                            @click="handleResend"
                        >
                            {{ isSending ? '发送中…' : '重新发送' }}
                        </button>
                        <p class="text-xs text-base-content/50 mt-1">
                            也请检查垃圾邮件文件夹
                        </p>
                    </div>

                    <button type="button" class="btn btn-ghost btn-sm w-full" :disabled="isSubmitting" @click="step = 'info'">
                        ← 修改注册信息
                    </button>
                </form>
            </template>

            <hr class="my-8">

            <p class="text-center text-sm">
                已有账号？
                <NuxtLink to="/auth/login" class="link link-primary">
                    登录
                </NuxtLink>
            </p>
        </div>
    </div>
</template>

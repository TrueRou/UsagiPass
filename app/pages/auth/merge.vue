<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })

const nuxtApp = useNuxtApp()
const leporidFetch = nuxtApp.$leporid as any
const { user, clear } = useUserSession()
const notificationsStore = useNotificationsStore()

const loginModalOpen = ref(false)

const secondaryAccount = ref<UserResponse | null>(null)
const secondaryToken = ref('')

type MergeSlot = 'current' | 'secondary'

const selection = reactive<{ source: MergeSlot, target: MergeSlot }>({
    source: 'current',
    target: 'secondary',
})

watch(secondaryAccount, (val) => {
    if (!val) {
        if (selection.source === 'secondary')
            selection.source = 'current'
        if (selection.target === 'secondary')
            selection.target = 'current'
    }
})

watch(() => selection.source, (val) => {
    if (val === selection.target)
        selection.target = val === 'current' ? 'secondary' : 'current'
})

watch(() => selection.target, (val) => {
    if (val === selection.source)
        selection.source = val === 'current' ? 'secondary' : 'current'
})

const sourceName = computed(() => (selection.source === 'current' ? user.value?.username : secondaryAccount.value?.username) || '未知')
const targetName = computed(() => (selection.target === 'current' ? user.value?.username : secondaryAccount.value?.username) || '未知')

const warnings = computed(() => ([
    `${sourceName.value} 的图片将合并到 ${targetName.value} 中。`,
    `${sourceName.value} 的个性化设置将覆盖到 ${targetName.value} 中。`,
    `${sourceName.value} 的旧账号系统设置将覆盖到 ${targetName.value} 中。`,
    `合并完成后 ${sourceName.value} 将被删除且无法恢复。`,
]))

const isReadyForMerge = computed(() => Boolean(secondaryAccount.value) && selection.source !== selection.target)

const confirmModalOpen = ref(false)
const confirmStage = ref<1 | 2>(1)
const isMerging = ref(false)

function openConfirmModal() {
    if (!isReadyForMerge.value)
        return
    confirmStage.value = 1
    confirmModalOpen.value = true
}

async function handleSecondaryLogin(payload: { username: string, password: string, strategy: 'LOCAL' | 'DIVING_FISH' | 'LXNS' }) {
    const tokenResponse = await leporidFetch('/api/auth/token', {
        method: 'POST',
        query: {
            grant_type: 'password',
            username: payload.username,
            password: payload.password,
            strategy: payload.strategy,
        },
    }) as UserAuthResponse

    const profile = await leporidFetch('/api/users/me', {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${tokenResponse.access_token}`,
        },
    }) as UserResponse

    secondaryAccount.value = profile
    secondaryToken.value = tokenResponse.access_token
    loginModalOpen.value = false
}

function setLoginModalOpen(value: boolean) {
    loginModalOpen.value = value
}

async function executeMerge() {
    if (!secondaryAccount.value)
        return
    isMerging.value = true
    try {
        await leporidFetch('/api/nuxt/auth/merge', {
            method: 'POST',
            body: {
                source: selection.source === 'current' ? undefined : secondaryToken.value,
                target: selection.target === 'current' ? undefined : secondaryToken.value,
            },
            showSuccessToast: true,
            successMessage: '合并成功',
        })
        await performPostMergeLogout()
    }
    finally {
        isMerging.value = false
        confirmModalOpen.value = false
    }
}

async function performPostMergeLogout() {
    try {
        await leporidFetch('/api/auth/logout', { method: 'POST' })
    }
    catch {}
    await clear()
    notificationsStore.addNotification({
        type: 'info',
        message: '合并完成，请使用新账号重新登录。',
    })
    await navigateTo('/auth/login', { replace: true })
}

function advanceConfirmation() {
    if (confirmStage.value === 1)
        confirmStage.value = 2
    else
        executeMerge()
}
</script>

<template>
    <div class="min-h-screen bg-base-200">
        <ModalMergeAccountLogin :open="loginModalOpen" @update:open="setLoginModalOpen" @confirm="handleSecondaryLogin" />

        <div class="mx-auto max-w-4xl px-4 py-10 space-y-6">
            <header class="space-y-2 text-center">
                <p class="text-xs uppercase tracking-[0.3em] text-primary">
                    账户合并
                </p>
                <h1 class="text-3xl font-bold">
                    合并你的 UsagiLab 账户
                </h1>
                <p class="text-sm text-base-content/70">
                    选择源账户与目标账户，所有内容将按所选方向迁移，此操作无法撤销。
                </p>
            </header>

            <div class="grid gap-4 md:grid-cols-2">
                <section class="rounded-box border border-base-300 bg-base-100 p-4 shadow-sm">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-xs uppercase tracking-widest text-base-content/60">
                                当前登录
                            </p>
                            <p class="text-xl font-semibold">
                                {{ user?.username }}
                            </p>
                            <p class="text-sm text-base-content/70">
                                {{ user?.email || '邮箱未设置' }}
                            </p>
                        </div>
                        <span class="badge badge-primary">使用中</span>
                    </div>
                    <div class="mt-4 space-y-2 text-sm">
                        <label class="flex items-center gap-2">
                            <input
                                v-model="selection.source" class="radio radio-error" name="source-current" type="radio" value="current"
                            >
                            <span>设为源账号</span>
                        </label>
                        <label class="flex items-center gap-2">
                            <input
                                v-model="selection.target" class="radio radio-success" name="target-current" type="radio" value="current"
                            >
                            <span>设为目标账号</span>
                        </label>
                    </div>
                </section>

                <section class="rounded-box border border-dashed border-base-300 bg-base-100 p-4 shadow-sm">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-xs uppercase tracking-widest text-base-content/60">
                                待合并账号
                            </p>
                            <p class="text-xl font-semibold">
                                {{ secondaryAccount?.username || '尚未关联' }}
                            </p>
                            <p class="text-sm text-base-content/70">
                                {{ secondaryAccount?.email || '邮箱未设置' }}
                            </p>
                        </div>
                        <span class="badge" :class="secondaryAccount ? 'badge-success' : 'badge-ghost'">
                            {{ secondaryAccount ? '已关联' : '待确认' }}
                        </span>
                    </div>

                    <div class="mt-4 space-y-3">
                        <div class="space-y-2 text-sm">
                            <label class="flex items-center gap-2">
                                <input
                                    v-model="selection.source" class="radio radio-error" name="source-secondary" type="radio" value="secondary"
                                    :disabled="!secondaryAccount"
                                >
                                <span>设为源账号</span>
                            </label>
                            <label class="flex items-center gap-2">
                                <input
                                    v-model="selection.target" class="radio radio-success" name="target-secondary" type="radio" value="secondary"
                                    :disabled="!secondaryAccount"
                                >
                                <span>设为目标账号</span>
                            </label>
                        </div>
                        <button class="btn btn-outline btn-sm" type="button" @click="loginModalOpen = true">
                            {{ secondaryAccount ? '重新关联该账号' : '关联另一个账号' }}
                        </button>
                    </div>
                </section>
            </div>

            <section class="rounded-box border border-warning bg-warning/10 p-4">
                <h2 class="text-lg font-semibold text-warning">
                    迁移警示
                </h2>
                <ul class="mt-3 space-y-2 text-sm">
                    <li v-for="message in warnings" :key="message" class="flex gap-2">
                        <span>•</span>
                        <span>{{ message }}</span>
                    </li>
                </ul>
            </section>

            <div class="pt-2">
                <button
                    class="btn btn-error w-full" type="button" :disabled="!isReadyForMerge || isMerging"
                    @click="openConfirmModal"
                >
                    <span v-if="isMerging" class="loading loading-spinner" />
                    <span>开始合并</span>
                </button>
            </div>
        </div>

        <div v-if="confirmModalOpen" class="modal modal-open">
            <div class="modal-box space-y-4">
                <h3 class="text-xl font-semibold text-error">
                    {{ confirmStage === 1 ? '请再次确认' : `${sourceName} 将被删除` }}
                </h3>
                <p class="text-sm text-base-content/70">
                    {{ confirmStage === 1 ? `你将把 ${sourceName} 的全部数据迁移到 ${targetName}。` : `迁移完成后 ${sourceName} 会被移除。` }}
                </p>
                <div class="modal-action">
                    <button class="btn btn-ghost" type="button" @click="confirmModalOpen = false">
                        取消
                    </button>
                    <button class="btn btn-error" type="button" :disabled="isMerging" @click="advanceConfirmation">
                        <span v-if="isMerging" class="loading loading-spinner" />
                        <span>{{ confirmStage === 1 ? '继续' : '立即合并' }}</span>
                    </button>
                </div>
            </div>
            <div class="modal-backdrop" @click="confirmModalOpen = false">
                取消
            </div>
        </div>
    </div>
</template>

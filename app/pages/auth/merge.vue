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

const mergeCopy = {
    badge: '账户合并',
    title: '合并你的 UsagiPass 账户',
    subtitle: '选择源账户与目标账户，所有内容将按所选方向迁移，此操作无法撤销。',
    currentLabel: '当前登录',
    secondaryLabel: '待合并账号',
    emailMissing: '邮箱未设置',
    inSession: '使用中',
    pending: '尚未关联',
    ready: '已关联',
    waiting: '待确认',
    relogin: '重新关联该账号',
    linkSecondary: '关联另一个账号',
    sourceRadio: '设为源账号',
    targetRadio: '设为目标账号',
    warningTitle: '迁移警示',
    callToAction: '开始合并',
    toastSuccess: '合并成功',
    loginNew: '合并完成，请使用新账号重新登录。',
    missing: '未知',
    summary: (source: string, target: string) => `源：${source} → 目标：${target}`,
    warnings: {
        images: (source: string, target: string) => `${source} 的图片将合并到 ${target} 中。`,
        preference: (source: string, target: string) => `${source} 的个性化设置将覆盖 ${target}。`,
        legacy: (source: string, target: string) => `${source} 的旧账号系统设置将覆盖 ${target}。`,
        deletion: (source: string) => `合并完成后 ${source} 将被删除且无法恢复。`,
    },
    confirm: {
        cancel: '取消',
        first: {
            title: '请再次确认',
            body: (source: string, target: string) => `你将把 ${source} 的全部数据迁移到 ${target}。`,
            cta: '继续',
        },
        second: {
            title: (source: string) => `${source} 将被删除`,
            body: (source: string) => `迁移完成后 ${source} 会被移除，请确保已经备份重要信息。`,
            cta: '立即合并',
        },
    },
}

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

const sourceName = computed(() => (selection.source === 'current' ? user.value?.username : secondaryAccount.value?.username) || mergeCopy.missing)
const targetName = computed(() => (selection.target === 'current' ? user.value?.username : secondaryAccount.value?.username) || mergeCopy.missing)

const warnings = computed(() => ([
    mergeCopy.warnings.images(sourceName.value, targetName.value),
    mergeCopy.warnings.preference(sourceName.value, targetName.value),
    mergeCopy.warnings.legacy(sourceName.value, targetName.value),
    mergeCopy.warnings.deletion(sourceName.value),
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
            successMessage: mergeCopy.toastSuccess,
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
        message: mergeCopy.loginNew,
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
                    {{ mergeCopy.badge }}
                </p>
                <h1 class="text-3xl font-bold">
                    {{ mergeCopy.title }}
                </h1>
                <p class="text-sm text-base-content/70">
                    {{ mergeCopy.subtitle }}
                </p>
            </header>

            <div class="grid gap-4 md:grid-cols-2">
                <section class="rounded-box border border-base-300 bg-base-100 p-4 shadow-sm">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-xs uppercase tracking-widest text-base-content/60">
                                {{ mergeCopy.currentLabel }}
                            </p>
                            <p class="text-xl font-semibold">
                                {{ user?.username }}
                            </p>
                            <p class="text-sm text-base-content/70">
                                {{ user?.email || mergeCopy.emailMissing }}
                            </p>
                        </div>
                        <span class="badge badge-primary">{{ mergeCopy.inSession }}</span>
                    </div>
                    <div class="mt-4 space-y-2 text-sm">
                        <label class="flex items-center gap-2">
                            <input
                                v-model="selection.source" class="radio radio-warning" name="source-current" type="radio" value="current"
                            >
                            <span>{{ mergeCopy.sourceRadio }}</span>
                        </label>
                        <label class="flex items-center gap-2">
                            <input
                                v-model="selection.target" class="radio radio-info" name="target-current" type="radio" value="current"
                            >
                            <span>{{ mergeCopy.targetRadio }}</span>
                        </label>
                    </div>
                </section>

                <section class="rounded-box border border-dashed border-base-300 bg-base-100 p-4 shadow-sm">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <p class="text-xs uppercase tracking-widest text-base-content/60">
                                {{ mergeCopy.secondaryLabel }}
                            </p>
                            <p class="text-xl font-semibold">
                                {{ secondaryAccount?.username || mergeCopy.pending }}
                            </p>
                            <p class="text-sm text-base-content/70">
                                {{ secondaryAccount?.email || mergeCopy.emailMissing }}
                            </p>
                        </div>
                        <span class="badge" :class="secondaryAccount ? 'badge-success' : 'badge-ghost'">
                            {{ secondaryAccount ? mergeCopy.ready : mergeCopy.waiting }}
                        </span>
                    </div>

                    <div class="mt-4 space-y-3">
                        <button class="btn btn-outline btn-sm" type="button" @click="loginModalOpen = true">
                            {{ secondaryAccount ? mergeCopy.relogin : mergeCopy.linkSecondary }}
                        </button>
                        <div class="space-y-2 text-sm">
                            <label class="flex items-center gap-2">
                                <input
                                    v-model="selection.source" class="radio radio-warning" name="source-secondary" type="radio" value="secondary"
                                    :disabled="!secondaryAccount"
                                >
                                <span>{{ mergeCopy.sourceRadio }}</span>
                            </label>
                            <label class="flex items-center gap-2">
                                <input
                                    v-model="selection.target" class="radio radio-info" name="target-secondary" type="radio" value="secondary"
                                    :disabled="!secondaryAccount"
                                >
                                <span>{{ mergeCopy.targetRadio }}</span>
                            </label>
                        </div>
                    </div>
                </section>
            </div>

            <section class="rounded-box border border-warning bg-warning/10 p-4">
                <h2 class="text-lg font-semibold text-warning">
                    {{ mergeCopy.warningTitle }}
                </h2>
                <ul class="mt-3 space-y-2 text-sm text-warning-content">
                    <li v-for="message in warnings" :key="message" class="flex gap-2">
                        <span>•</span>
                        <span>{{ message }}</span>
                    </li>
                </ul>
            </section>

            <div class="rounded-box border border-base-300 bg-base-100 p-4 text-sm text-base-content/80">
                <p>
                    {{ mergeCopy.summary(sourceName, targetName) }}
                </p>
            </div>

            <div class="pt-2">
                <button
                    class="btn btn-error w-full" type="button" :disabled="!isReadyForMerge || isMerging"
                    @click="openConfirmModal"
                >
                    <span v-if="isMerging" class="loading loading-spinner" />
                    <span>{{ mergeCopy.callToAction }}</span>
                </button>
            </div>
        </div>

        <div v-if="confirmModalOpen" class="modal modal-open">
            <div class="modal-box space-y-4">
                <h3 class="text-xl font-semibold text-error">
                    {{ confirmStage === 1 ? mergeCopy.confirm.first.title : mergeCopy.confirm.second.title(sourceName) }}
                </h3>
                <p class="text-sm text-base-content/70">
                    {{ confirmStage === 1 ? mergeCopy.confirm.first.body(sourceName, targetName) : mergeCopy.confirm.second.body(sourceName) }}
                </p>
                <div class="modal-action">
                    <button class="btn btn-ghost" type="button" @click="confirmModalOpen = false">
                        {{ mergeCopy.confirm.cancel }}
                    </button>
                    <button class="btn btn-error" type="button" :disabled="isMerging" @click="advanceConfirmation">
                        <span v-if="isMerging" class="loading loading-spinner" />
                        <span>{{ confirmStage === 1 ? mergeCopy.confirm.first.cta : mergeCopy.confirm.second.cta }}</span>
                    </button>
                </div>
            </div>
            <div class="modal-backdrop" @click="confirmModalOpen = false">
                {{ mergeCopy.confirm.cancel }}
            </div>
        </div>
    </div>
</template>

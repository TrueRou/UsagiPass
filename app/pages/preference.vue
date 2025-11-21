<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })
useHead({
    title: '偏好设置 - UsagiPass',
})

const { t } = useI18n()
const { $leporid } = useNuxtApp()
const { loggedIn, user, clear } = useUserSession()
const notificationsStore = useNotificationsStore()

const { data: profileDataRaw } = await useLeporid<UserProfile>('/api/nuxt/profile')
const { data: serversData } = await useLeporid<Server[]>('/api/nuxt/servers')
const { data: imageAspect } = await useLeporid<ImageAspect>('/api/images/aspects/id-1-ff')

const profileData = ref<UserProfile>()

watch(profileDataRaw, val => profileData.value = val, { immediate: true })

type PreferenceForm = Omit<UserPreference, 'user_id'>

const serverMap = computed(() => {
    const map = new Map<number, Server>()
    serversData.value?.forEach(server => map.set(server.id, server))
    return map
})

type ImageMapKey = 'character' | 'mask' | 'background' | 'frame'

const imageFieldMap: Record<ImageMapKey, keyof PreferenceForm> = {
    character: 'characterId',
    mask: 'maskId',
    background: 'backgroundId',
    frame: 'frameId',
}

function clearImage(key: ImageMapKey) {
    if (profileData.value) {
        Object.assign(profileData.value.preference, { [imageFieldMap[key]]: '' })
    }
}

async function matchCharacterMetadata() {
    const response: {
        mask_image?: ImageResponse
        source: string
        character_name?: string
        version?: string
    } = await $leporid('/api/nuxt/image/metadata', {
        method: 'GET',
        query: {
            id: profileData.value?.preference.characterId,
        },
    })

    let message = '未能匹配到任何数据。'

    if (response.source) {
        message = `数据来源： ${response.source} \n`

        if (response.mask_image && profileData.value) {
            profileData.value.preference.maskId = response.mask_image.id
            message += `遮罩图层： ${response.mask_image.metadata_id} \n`
        }

        if (response.character_name && profileData.value) {
            profileData.value.preference.characterName = response.character_name
            message += `立绘名称： ${response.character_name} \n`
        }

        if (response.version && profileData.value) {
            profileData.value.preference.maimaiVersion = response.version
            message += `游戏版本： ${response.version} \n`
        }
    }

    notificationsStore.addNotification({ type: response.source ? 'success' : 'warning', message, duration: 5000 })
}

async function handleLogout() {
    await clear()
    notificationsStore.addNotification({
        type: 'info',
        message: '已退出账户，请重新登录。',
    })
    await navigateTo('/auth/login')
}

// 图片选择逻辑

const selectorTarget = ref<ImageMapKey | null>(null)
const selectorOpen = ref(false)

function openImageSelector(key: ImageMapKey) {
    selectorTarget.value = key
    selectorOpen.value = true
}

function handleSelectorVisibility(value: boolean) {
    selectorOpen.value = value
    if (!value) {
        selectorTarget.value = null
    }
}

function handleImageSelect(image: ImageResponse) {
    if (selectorTarget.value) {
        if (profileData.value)
            Object.assign(profileData.value?.preference, { [imageFieldMap[selectorTarget.value]]: image.id })
    }
}

function showMatchCharacterMetadataHelp() {
    const notificationsStore = useNotificationsStore()
    notificationsStore.addNotification({
        type: 'info',
        message: '匹配数据功能说明：\n根据当前选择的角色立绘，自动匹配游戏版本、立绘名称、遮罩图层。',
        duration: 10000,
    })
}

// 账户系统逻辑

const addAccountOpen = ref(false)

function openAddAccount() {
    addAccountOpen.value = true
}

function handleAddAccountVisibility(value: boolean) {
    addAccountOpen.value = value
}

function handleAddAccount(server: Server, credentials: string) {
    if (profileData.value) {
        profileData.value.accounts.push({
            id: String(crypto.randomUUID()),
            userId: profileData.value.preference.userId,
            serverId: server.id,
            credentials,
            enabled: true,
            createdAt: new Date(),
            updatedAt: new Date(),
        })
        addAccountOpen.value = false
    }
}

function removeAccount(accountId: string) {
    if (profileData.value) {
        profileData.value.accounts = profileData.value.accounts.filter(account => account.id !== accountId)
    }
}

// 保存相关逻辑

const isSaving = ref(false)

async function handleSave() {
    isSaving.value = true
    try {
        profileData.value = await useNuxtApp().$leporid('/api/nuxt/profile', {
            method: 'PUT',
            body: profileData.value,
            showSuccessToast: true,
            successMessage: '偏好设置已保存',
        })
    }
    finally {
        setTimeout(() => isSaving.value = false, 500) // 保证最短等待 500 毫秒
    }
}

function goToPrev() {
    watch(() => isSaving.value, (newVal, oldVal) => {
        if (oldVal === true && newVal === false)
            useRouter().go(-1)
    })
}
</script>

<template>
    <div class="min-h-screen bg-base-200">
        <ImageSelector
            v-if="selectorTarget && imageAspect"
            :open="selectorOpen" :aspect="imageAspect" :title="selectorTarget ? t(`images.${selectorTarget}.title`) : t('images.title-default')"
            confirm-label="使用该图片" :initial-filters="selectorTarget ? [selectorTarget] : []" @update:open="handleSelectorVisibility"
            @select="handleImageSelect"
        />
        <ModalAddAccount
            :open="addAccountOpen" :servers="serversData || []" @update:open="handleAddAccountVisibility"
            @confirm="handleAddAccount"
        />
        <div class="mx-auto w-full max-w-6xl px-4 py-4 lg:py-10">
            <form v-if="profileData && serversData" class="space-y-4" @submit.prevent="handleSave">
                <!-- 已登录用户 -->
                <section class="rounded-box border border-base-200 bg-base-100 p-4 shadow-sm">
                    <div class="flex flex-wrap items-center gap-4">
                        <div class="avatar">
                            <div class="w-10 rounded-full border border-base-200">
                                <img src="../assets/icons/logo.webp">
                            </div>
                        </div>
                        <div class="flex-1">
                            <p class="text-md font-semibold">
                                {{ user?.username }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ user?.email }}
                            </p>
                        </div>
                        <div class="flex items-center gap-1">
                            <button class="btn btn-outline btn-sm" type="button" :disabled="!loggedIn" @click="handleLogout">
                                <span>登出</span>
                            </button>
                            <details class="dropdown dropdown-end">
                                <summary class="btn btn-ghost btn-sm">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01" />
                                    </svg>
                                </summary>
                                <ul class="menu mt-1 dropdown-content bg-base-300 rounded-box z-1 w-52 p-2 shadow-sm">
                                    <li>
                                        <NuxtLink class="justify-between" to="/auth/merge">
                                            合并账户
                                            <span class="badge badge-outline badge-xs">Beta</span>
                                        </NuxtLink>
                                    </li>
                                </ul>
                            </details>
                        </div>
                    </div>
                </section>

                <!-- 偏好设置标题 -->
                <div class="divider my-2">
                    {{ t("sections.preference") }}
                </div>

                <!-- 偏好设置表单 -->
                <div class="grid gap-4 md:grid-cols-2">
                    <!-- 玩家名称 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.displayName.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.displayName.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.displayName" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.displayName.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 卡面标签 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.simplifiedCode.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.simplifiedCode.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.simplifiedCode" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.simplifiedCode.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 好友代码 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.friendCode.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.friendCode.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.friendCode" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.friendCode.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 游戏版本 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.maimaiVersion.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.maimaiVersion.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.maimaiVersion" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.maimaiVersion.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 玩家评分 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.dxRating.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.dxRating.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.dxRating" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.dxRating.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 立绘名称 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.characterName.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.characterName.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.characterName" class="input input-bordered flex-1"
                                type="text" :placeholder="t('fields.characterName.placeholder')"
                            >
                        </div>
                    </div>

                    <!-- 角色立绘区颜色 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.charaInfoColor.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.charaInfoColor.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.charaInfoColor" class="input input-bordered flex-1"
                                type="color"
                            >
                        </div>
                    </div>

                    <!-- 玩家信息区颜色 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.playerInfoColor.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t(`fields.playerInfoColor.helper`) }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3">
                            <input
                                v-model="profileData.preference.playerInfoColor" class="input input-bordered flex-1"
                                type="color"
                            >
                        </div>
                    </div>

                    <!-- 二维码尺寸 -->
                    <div class="form-control flex flex-col gap-2 rounded-lg px-4 py-3">
                        <label>
                            <p class="font-medium text-sm">
                                {{ t("fields.qrSize.label") }}
                            </p>
                            <p class="text-xs text-base-content/60">
                                {{ t("fields.qrSize.helper") }}
                            </p>
                        </label>
                        <div class="flex items-center gap-3 h-10">
                            <input
                                v-model="profileData.preference.qrSize" class="range range-primary flex-1" type="range" min="8"
                                max="40"
                            >
                            <span class="badge badge-lg">
                                {{ profileData.preference.qrSize }}
                                {{ t("fields.qrSize.unit") }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- 显示设置标题 -->
                <div class="divider my-2">
                    {{ t("sections.display") }}
                </div>

                <!-- 显示设置表单 -->
                <div class="grid gap-4 md:grid-cols-2">
                    <!-- 显示玩家名称 -->
                    <div class="form-control flex items-center justify-between gap-4 rounded-lg px-4 py-3">
                        <div>
                            <p class="font-medium text-sm">
                                {{ t("fields.showDisplayName.label") }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ t("fields.showDisplayName.helper") }}
                            </p>
                        </div>
                        <input
                            v-model="profileData.preference.showDisplayName" class="toggle toggle-primary"
                            type="checkbox"
                        >
                    </div>

                    <!-- 显示好友代码 -->
                    <div class="form-control flex items-center justify-between gap-4 rounded-lg px-4 py-3">
                        <div>
                            <p class="font-medium text-sm">
                                {{ t("fields.showFriendCode.label") }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ t("fields.showFriendCode.helper") }}
                            </p>
                        </div>
                        <input
                            v-model="profileData.preference.showFriendCode" class="toggle toggle-primary"
                            type="checkbox"
                        >
                    </div>

                    <!-- 显示玩家评分 -->
                    <div class="form-control flex items-center justify-between gap-4 rounded-lg px-4 py-3">
                        <div>
                            <p class="font-medium text-sm">
                                {{ t("fields.showDxRating.label") }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ t("fields.showDxRating.helper") }}
                            </p>
                        </div>
                        <input
                            v-model="profileData.preference.showDxRating" class="toggle toggle-primary"
                            type="checkbox"
                        >
                    </div>

                    <!-- 显示日期 -->
                    <div class="form-control flex items-center justify-between gap-4 rounded-lg px-4 py-3">
                        <div>
                            <p class="font-medium text-sm">
                                {{ t("fields.showDate.label") }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ t("fields.showDate.helper") }}
                            </p>
                        </div>
                        <input
                            v-model="profileData.preference.showDate" class="toggle toggle-primary"
                            type="checkbox"
                        >
                    </div>

                    <!-- 开启遮罩图层 -->
                    <div class="form-control flex items-center justify-between gap-4 rounded-lg px-4 py-3">
                        <div>
                            <p class="font-medium text-sm">
                                {{ t("fields.enableMask.label") }}
                            </p>
                            <p class="text-xs text-base-content/70">
                                {{ t("fields.enableMask.helper") }}
                            </p>
                        </div>
                        <input
                            v-model="profileData.preference.enableMask" class="toggle toggle-primary"
                            type="checkbox"
                        >
                    </div>
                </div>

                <!-- 图片设置标题 -->
                <div class="divider my-2">
                    {{ t("sections.images") }}
                </div>

                <!-- 图片设置表单 -->
                <div class="grid gap-4 md:grid-cols-2">
                    <!-- 角色立绘 -->
                    <AppPreferImage
                        :image-id="profileData.preference.characterId"
                        :label="t('images.character.label')"
                        :helper="t('images.character.helper')"
                        :alt="t('images.character.label')"
                        :allow-clear="true"
                        @select="openImageSelector('character')"
                        @clear="clearImage('character')"
                    >
                        <template #actions>
                            <div class="flex items-center gap-1">
                                <button class="btn btn-sm btn-outline" type="button" @click="matchCharacterMetadata">
                                    匹配数据
                                </button>
                                <button class="btn btn-ghost btn-xs btn-circle" type="button" title="查看说明" @click="showMatchCharacterMetadataHelp">
                                    <span class="text-xs">?</span>
                                </button>
                            </div>
                        </template>
                    </AppPreferImage>

                    <!-- 遮罩图层 -->
                    <AppPreferImage
                        :image-id="profileData.preference.maskId"
                        :label="t('images.mask.label')"
                        :helper="t('images.mask.helper')"
                        :alt="t('images.mask.label')"
                        :allow-clear="true"
                        @select="openImageSelector('mask')"
                        @clear="clearImage('mask')"
                    />

                    <!-- 背景 -->
                    <AppPreferImage
                        :image-id="profileData.preference.backgroundId"
                        :label="t('images.background.label')"
                        :helper="t('images.background.helper')"
                        :alt="t('images.background.label')"
                        :allow-clear="false"
                        @select="openImageSelector('background')"
                        @clear="clearImage('background')"
                    />

                    <!-- 边框 -->
                    <AppPreferImage
                        :image-id="profileData.preference.frameId"
                        :label="t('images.frame.label')"
                        :helper="t('images.frame.helper')"
                        :alt="t('images.frame.label')"
                        :allow-clear="true"
                        @select="openImageSelector('frame')"
                        @clear="clearImage('frame')"
                    />
                </div>

                <!-- 账号设置标题 -->
                <div class="divider my-2">
                    {{ t("sections.accounts") }}
                </div>

                <!-- 账号设置表单 -->
                <div class="flex flex-col flex-auto gap-4">
                    <button
                        class="btn btn-outline" type="button"
                        @click="openAddAccount"
                    >
                        新增账号
                    </button>

                    <div
                        v-if="profileData.accounts.length === 0"
                        class="rounded-lg border border-dashed border-base-200 p-8 text-center text-sm text-base-content/60"
                    >
                        暂无账号，请新增账号
                    </div>

                    <div v-else class="space-y-4">
                        <div
                            v-for="account in profileData.accounts" :key="account.id"
                            class="space-y-4 rounded-xl border bg-base-200 text-base-content/80 p-4"
                        >
                            <div class="flex gap-3 items-center justify-between">
                                <div>
                                    <p class="text-base font-semibold">
                                        {{ serverMap.get(account.serverId)?.name || t("accounts.fallback-name") }}
                                    </p>
                                    <p class="text-xs text-base-content/60">
                                        {{ serverMap.get(account.serverId)?.description || t("accounts.fallback-desc") }}
                                    </p>
                                </div>
                                <div class="flex items-center gap-3">
                                    <label class="flex items-center gap-2 text-sm">
                                        <input
                                            v-model="account.enabled" class="toggle toggle-primary"
                                            type="checkbox"
                                        >
                                    </label>
                                    <button
                                        class="btn btn-ghost btn-sm text-error" type="button"
                                        @click="removeAccount(account.id)"
                                    >
                                        删除
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <footer class="flex justify-end">
                    <button class="btn btn-primary w-full md:w-auto" type="submit" :disabled="isSaving" @click.stop="goToPrev()">
                        <span v-if="isSaving" class="loading loading-spinner" />
                        <span>保存修改</span>
                    </button>
                </footer>
            </form>
        </div>
    </div>
</template>

<i18n lang="yaml">
zh-CN:
  sections:
    preference: 偏好设置
    display: 显示设置
    images: 图片设置
    accounts: 账号设置
  fields:
    displayName:
      label: 玩家名称
      helper: 覆盖卡面右上方显示的玩家名称
      placeholder: 留空以自动获取
    simplifiedCode:
      label: 卡面标签
      helper: 覆盖卡面底栏左侧显示的文字内容
      placeholder: 留空以自动获取
    friendCode:
      label: 好友代码
      helper: 覆盖卡面右上方显示的好友代码
      placeholder: 留空以自动获取
    characterName:
      label: 立绘名称
      helper: 覆盖卡面左下方显示的角色立绘名称
      placeholder: 留空以隐藏
    maimaiVersion:
      label: 游戏版本
      helper: 覆盖卡面底栏右侧显示的版本信息
      placeholder: 留空以自动获取
    dxRating:
      label: 玩家评分
      helper: 覆盖卡面顶栏右侧显示的玩家评分
      placeholder: 留空以自动获取
    qrSize:
      label: 二维码尺寸
      helper: 调整展示在卡面右下方的二维码大小
      unit: px
    charaInfoColor:
      label: 角色立绘区颜色
      helper: 角色立绘信息区的背景颜色
    playerInfoColor:
      label: 玩家信息区颜色
      helper: 玩家信息区的背景颜色
    showDisplayName:
      label: 显示玩家名称
      helper: 是否显示右上方玩家名称
    showFriendCode:
      label: 显示好友代码
      helper: 是否显示右上方好友代码
    showDxRating:
      label: 显示玩家评分
      helper: 是否显示顶栏右侧玩家评分
    showDate:
      label: 显示日期
      helper: 是否显示左下方日期
    enableMask:
      label: 开启遮罩图层
      helper: 是否在角色立绘上应用遮罩图层渐变效果
    account:
      server: 选择服务器
      credentials: 账号凭据
  images:
    title-default: 选择图片
    character:
      label: 角色立绘
      title: 选择角色立绘
      helper: 卡面正面展示的角色形象
    mask:
      label: 遮罩图层
      title: 选择遮罩图层
      helper: 覆盖在立绘上的装饰或遮挡层
    background:
      label: 背景
      title: 选择背景
      helper: 角色背后展示的背景
    frame:
      label: 边框
      title: 选择边框
      helper: 包裹卡面的装饰框体
    passname:
      label: 名牌横幅
      title: 选择名牌横幅
      helper: 卡片顶部显示名牌的横幅
</i18n>

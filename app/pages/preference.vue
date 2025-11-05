<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })

const { t } = useI18n()
const { img } = useUtils()

const { data: profileDataRaw, pending: profilePending } = await useLeporid<UserProfile>('/api/nuxt/profile')
const { data: serversData, pending: serversPending } = await useLeporid<Server[]>('/api/nuxt/servers')

const isInitialLoading = computed(() => profilePending.value || serversPending.value)
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

const imageCardItems = computed(() =>
    Object.keys(imageFieldMap).map(key => key as ImageMapKey).map((key) => {
        const raw = profileData.value?.preference[imageFieldMap[key]] as string | undefined
        return {
            key,
            field: imageFieldMap[key],
            src: raw ? img(raw) : '',
            selected: Boolean(raw),
        }
    }),
)

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
            successMessage: t('toast.save-success'),
        })
    }
    finally {
        isSaving.value = false
    }
}
</script>

<template>
    <div class="min-h-screen bg-base-200">
        <ImageSelector
            v-if="selectorTarget"
            :open="selectorOpen" aspect-id="id-1-ff" :title="selectorTarget ? t(`images.${selectorTarget}.title`) : t('images.title-default')"
            :confirm-label="t('actions.use-image')" :initial-filters="selectorTarget ? [selectorTarget] : []" @update:open="handleSelectorVisibility"
            @select="handleImageSelect"
        />
        <ModalAddAccount
            :open="addAccountOpen" :servers="serversData || []" @update:open="handleAddAccountVisibility"
            @confirm="handleAddAccount"
        />
        <div class="mx-auto w-full max-w-6xl px-4 py-4 lg:py-10">
            <div v-if="isInitialLoading" class="flex flex-col items-center gap-4 py-16 text-base-content/60">
                <span class="loading loading-spinner loading-lg" />
                <p>{{ t("loading.initial") }}</p>
            </div>

            <form v-else-if="profileData && serversData" class="space-y-4" @submit.prevent="handleSave">
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
                        <div class="flex items-center gap-3 h-[40px]">
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
                </div>

                <!-- 图片设置标题 -->
                <div class="divider my-2">
                    {{ t("sections.images") }}
                </div>

                <!-- 图片设置表单 -->
                <div class="grid gap-4 md:grid-cols-2">
                    <div v-for="item in imageCardItems" :key="item.key" class="rounded-xl p-4">
                        <div class="flex items-start gap-3">
                            <div class="flex w-16 items-center justify-center overflow-hidden rounded-lg border border-base-200">
                                <img v-if="item.src" :src="item.src" :alt="t(`images.${item.key}.label`)" class="h-full w-full object-cover" loading="lazy">
                                <span v-else class="text-xs text-base-content/40">{{ t("preview.empty") }}</span>
                            </div>
                            <div class="flex-1 space-y-1">
                                <p class="text-sm font-semibold">
                                    {{ t(`images.${item.key}.label`) }}
                                </p>
                                <p class="text-xs text-base-content/60">
                                    {{ t(`images.${item.key}.helper`) }}
                                </p>
                                <div class="flex flex-wrap gap-2 pt-1">
                                    <button class="btn btn-sm btn-primary" type="button" @click="openImageSelector(item.key)">
                                        {{ item.selected ? t("actions.replace-image") : t("actions.choose-image") }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
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
                        {{ t("actions.add-account") }}
                    </button>

                    <div
                        v-if="profileData.accounts.length === 0"
                        class="rounded-lg border border-dashed border-base-200 p-8 text-center text-sm text-base-content/60"
                    >
                        {{ t("accounts.empty") }}
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
                                        {{ t("actions.remove-account") }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <footer class="flex justify-end">
                    <button class="btn btn-primary w-full md:w-auto" type="submit" :disabled="isSaving">
                        <span v-if="isSaving" class="loading loading-spinner" />
                        <span>{{ t("actions.save") }}</span>
                    </button>
                </footer>
            </form>
        </div>
    </div>
</template>

<i18n lang="yaml">
en-GB:
  loading:
    initial: Loading Profile...
  sections:
    preference: Preference Settings
    display: Display Settings
    images: Image Settings
    accounts: Account Settings
  fields:
    displayName:
      label: Player Name
      helper: Override the player name displayed in the upper right of the card
      placeholder: Leave blank to auto-fetch
    simplifiedCode:
      label: Card Label
      helper: Override the text content displayed on the left side of the bottom bar of the card
      placeholder: Leave blank to auto-fetch
    friendCode:
      label: Friend Code
      helper: Override the friend code displayed in the upper right of the card
      placeholder: Leave blank to auto-fetch
    characterName:
      label: Character Portrait Name
      helper: Override the character portrait name displayed in the lower left of the card
      placeholder: Leave blank to hide
    maimaiVersion:
      label: Game Version
      helper: Override the version information displayed on the right side of the bottom bar of the card
      placeholder: Leave blank to auto-fetch
    dxRating:
      label: Player Rating
      helper: Override the player rating displayed on the right side of the top bar of the card
      placeholder: Leave blank to auto-fetch
    qrSize:
      label: QR Code Size
      helper: Adjust the size of the QR code displayed in the lower right of the card
      unit: px
    charaInfoColor:
      label: Character Info Area Color
      helper: Background color of the character area
    playerInfoColor:
      label: Player Info Area Color
      helper: Background color of the player area
    showDisplayName:
      label: Show Player Name
      helper: Whether to display the player name in the upper right
    showFriendCode:
      label: Show Friend Code
      helper: Whether to display the friend code in the upper right
    showDxRating:
      label: Show Player Rating
      helper: Whether to display the player rating on the right side of the top bar
    showDate:
      label: Show Date
      helper: Whether to display the date in the lower left
    account:
      server: Select Server
      credentials: Account Credentials
  images:
    title-default: Select Images
    character:
      label: Character Portrait
      title: Select Character Portrait
      helper: Character portrait of card front
    mask:
      label: Mask Layer
      title: Select Mask Layer
      helper: Decorative or obscuring overlays on character portrait
    background:
      label: Background
      title: Select Background Image
      helper: Background Image of character
    frame:
      label: Frame
      title: Select Frame Image
      helper: Decorative card frame
    passname:
      label: Banner
      title: Select Banner Image
      helper: Banner at the top of the card
    empty: Not Selected
    placeholder: Selecting an image will display its path
    status:
      assigned: Selected images will be applied to the card
      empty: Not selected image
      badge: Enable
  actions:
    choose-image: Choose
    replace-image: Replace
    clear-image: Clear
    add-account: Add
    remove-account: Remove
    use-image: Use
    save: Save
  accounts:
    empty: No account found. Please create one
    fallback-name: Not Server Selected
    fallback-desc: Please Select An Server to view more info
  toast:
    save-success: Preference Saved
zh-CN:
  loading:
    initial: 正在加载个人资料...
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
    empty: 暂未选择
    placeholder: 选择图片后将显示路径
    status:
      assigned: 已选中的图片将用于卡面
      empty: 尚未选择图片
      badge: 已启用
  actions:
    choose-image: 选择图片
    replace-image: 更换图片
    clear-image: 清除选择
    add-account: 新增账号
    remove-account: 删除
    use-image: 使用该图片
    save: 保存修改
  accounts:
    empty: 暂无账号，请新增账号
  toast:
    save-success: 偏好设置已保存
</i18n>

<script setup lang="ts">
const props = defineProps<{
    open: boolean
    aspectId: string
    initialFilters?: string[]
    pageSize?: number
    title?: string
    confirmLabel?: string
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'select', payload: ImageResponse): void
}>()

const { t } = useI18n()
const { img } = useUtils()

const {
    aspect,
    fetchAspect,
    images,
    loading,
    list,
    pageNumber,
    totalRow,
    totalPage,
    representativeLabels,
    updateImage,
    deleteImage,
    uploadImage,
    setAspectId,
} = useImages({ aspectId: props.aspectId, pageSize: props.pageSize, initialFilters: props.initialFilters })

const activeSecondary = ref<string[]>([])
const searchKeyword = ref('')
const selectedImage = ref<ImageResponse | null>(null)
const openUploader = ref(false)
const deleteTarget = ref<ImageResponse | null>(null)
const pending = ref(false)

const title = computed(() => props.title ?? t('title-default'))
const confirmButtonText = computed(() => props.confirmLabel ?? t('actions.confirm'))

const imageKey = (image: ImageResponse) => image.id

const imageUrl = (image: ImageResponse) => img(image.id)

function isSelected(image: ImageResponse) {
    if (!selectedImage.value)
        return false
    return image.id === selectedImage.value.id
}

function close() {
    openUploader.value = false
    deleteTarget.value = null
    emit('update:open', false)
}

function updateSelection(image: ImageResponse) {
    selectedImage.value = image
}

function clearSearch() {
    searchKeyword.value = ''
}

async function prevPage() {
    if (pageNumber.value <= 1)
        return
    await list({ pageNumber: pageNumber.value - 1, filters: activeSecondary.value })
    selectedImage.value = null
}

async function nextPage() {
    if (pageNumber.value >= totalPage.value)
        return
    console.warn('next page: ', pageNumber.value + 1)
    await list({ pageNumber: pageNumber.value + 1, filters: activeSecondary.value })
    selectedImage.value = null
}

async function jumpToPage(event: Event) {
    const target = event.target as HTMLInputElement
    const value = Number.parseInt(target.value, 10)
    if (!Number.isFinite(value))
        return
    const page = Math.min(Math.max(value, 1), totalPage.value)
    await list({ pageNumber: page, filters: activeSecondary.value })
    selectedImage.value = null
}

function confirmSelection() {
    if (!selectedImage.value)
        return
    emit('select', selectedImage.value)
    close()
}

async function handleRename({ image, name }: { image: ImageResponse, name: string }) {
    pending.value = true
    try {
        await updateImage(image.id, {
            name,
            description: image.description,
            visibility: image.visibility,
            labels: image.labels ?? [],
        })
    }
    finally {
        pending.value = false
    }
}

function confirmDelete(image: ImageResponse) {
    deleteTarget.value = image
}

async function handleDelete() {
    if (!deleteTarget.value)
        return
    pending.value = true
    try {
        await deleteImage(deleteTarget.value.id)
        if (selectedImage.value && selectedImage.value.id === deleteTarget.value.id) {
            selectedImage.value = null
        }
        deleteTarget.value = null
    }
    finally {
        pending.value = false
    }
}

function handleUploaded(image: ImageResponse) {
    selectedImage.value = image
}

watch(() => props.open, async (isOpen) => {
    if (isOpen) {
        setAspectId(props.aspectId)
        await fetchAspect()
        await list({ pageNumber: 1, filters: activeSecondary.value })
    }
    else {
        selectedImage.value = null
        activeSecondary.value = []
    }
}, { immediate: true })

watch([activeSecondary, searchKeyword], async () => {
    await list({ filters: activeSecondary.value })
})
</script>

<template>
    <dialog v-if="open" class="modal modal-open">
        <div class="modal-box max-w-6xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4" @click.prevent="close">
                    ✕
                </button>
            </form>
            <div class="space-y-6">
                <header class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h2 class="text-2xl font-semibold">
                            {{ title }}
                        </h2>
                        <p v-if="aspect" class="text-sm text-base-content/70">
                            {{ t('aspect-format', {
                                name: aspect.name,
                                ratio:
                                    `${aspect.ratioWidthUnit}:${aspect.ratioHeightUnit}`,
                            }) }}
                        </p>
                    </div>
                </header>

                <section class="space-y-4">
                    <div class="flex flex-wrap gap-3 items-center">
                        <form
                            class="join filter" role="radiogroup" aria-label="Secondary filter" @submit.prevent
                            @reset.prevent
                        >
                            <input
                                v-for="val in representativeLabels" :key="val" v-model="activeSecondary" type="checkbox"
                                name="secondary-filter" class="btn btn-sm join-item" :value="val" :aria-label="val"
                            >
                        </form>
                        <div class="join w-full">
                            <input
                                v-model="searchKeyword" type="search" class="input input-bordered join-item flex-1"
                                :placeholder="t('search-placeholder')"
                            >
                            <button class="btn join-item" type="button" @click="clearSearch">
                                {{ t('clear') }}
                            </button>
                        </div>
                    </div>
                </section>

                <section class="min-h-[320px]">
                    <div v-if="loading" class="flex items-center justify-center py-16">
                        <span class="loading loading-spinner loading-lg" />
                    </div>
                    <div v-else>
                        <div
                            v-if="images.length === 0"
                            class="rounded-lg border border-dashed p-10 text-center space-y-4"
                        >
                            <p class="text-base-content/60">
                                {{ t('empty') }}
                            </p>
                            <button class="btn btn-primary" type="button" @click="openUploader = true">
                                {{ t('actions.upload') }}
                            </button>
                        </div>
                        <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                            <ImageCard
                                v-for="image in images" :key="imageKey(image)" :image="image"
                                :image-url="imageUrl(image)" :selected="isSelected(image)"
                                :disabled="pending" :hided-labels="initialFilters" @select="updateSelection"
                                @rename="handleRename"
                                @delete="confirmDelete"
                            />
                        </div>
                    </div>
                </section>

                <section class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div class="text-sm text-base-content/70">
                        {{ t('pagination-status', { page: pageNumber, totalPage, totalRow }) }}
                    </div>
                    <div class="join">
                        <button class="btn join-item" type="button" :disabled="pageNumber <= 1" @click="prevPage">
                            {{ t('pagination-prev') }}
                        </button>
                        <input
                            class="input input-bordered join-item w-16 text-center" type="number" :value="pageNumber"
                            min="1" :max="totalPage" @change="jumpToPage($event)"
                        >
                        <button
                            class="btn join-item" type="button" :disabled="pageNumber >= totalPage"
                            @click="nextPage"
                        >
                            {{ t('pagination-next') }}
                        </button>
                    </div>
                </section>
            </div>

            <div class="modal-action">
                <button class="btn" type="button" @click="close">
                    {{ t('actions.cancel') }}
                </button>
                <button
                    class="btn btn-primary" type="button" :disabled="!selectedImage || pending"
                    @click="confirmSelection"
                >
                    <span v-if="pending" class="loading loading-spinner" />
                    <span>{{ confirmButtonText }}</span>
                </button>
            </div>
        </div>
    </dialog>

    <ImageUploader
        v-if="open" :open="openUploader" :aspect="aspect" :aspect-id="props.aspectId"
        :suggested-labels="representativeLabels" :upload="uploadImage" @update:open="val => openUploader = val"
        @uploaded="handleUploaded"
    />

    <dialog v-if="deleteTarget" class="modal modal-open">
        <div class="modal-box">
            <h3 class="font-semibold text-lg mb-4">
                {{ t('delete-title') }}
            </h3>
            <p>{{ t('delete-message', { name: deleteTarget.name }) }}</p>
            <div class="modal-action">
                <button class="btn" type="button" @click="deleteTarget = null">
                    {{ t('actions.cancel') }}
                </button>
                <button class="btn btn-error" type="button" :disabled="pending" @click="handleDelete">
                    <span v-if="pending" class="loading loading-spinner" />
                    <span>{{ t('actions.delete') }}</span>
                </button>
            </div>
        </div>
    </dialog>
</template>

<i18n lang="yaml">
en-GB:
  title-default: Select an image
  aspect-format: "Aspect: {name} · {ratio}"
  actions:
    upload: Upload new image
    cancel: Cancel
    confirm: Use this image
    delete: Delete
  search-placeholder: Search by name
  clear: Clear
  empty: No images match your filters yet.
  custom-placeholder: Upload your own image
  pagination-status: "Page {page} of {totalPage}, total {total} images"
  pagination-prev: Previous
  pagination-next: Next
  delete-title: Delete image
  delete-message: "Are you sure you want to delete “{name}”?"

zh-CN:
  title-default: 选择图片
  aspect-format: "比例：{name} · {ratio}"
  actions:
    upload: 上传新图片
    cancel: 取消
    confirm: 使用此图片
    delete: 删除
  search-placeholder: 按名称搜索
  clear: 清空
  empty: 暂无符合条件的图片
  custom-placeholder: 上传你的专属图片
  pagination-status: "第 {page} / {totalPage} 页，共 {totalRow} 张图片"
  pagination-prev: 上一页
  pagination-next: 下一页
  delete-title: 删除图片
  delete-message: "确定要删除“{name}”吗？"
</i18n>

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
const { imgPreview } = useUtils()

const {
    aspect,
    fetchAspect,
    images,
    loading,
    list,
    pageNumber,
    totalRow,
    totalPage,
    activeFilters,
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

const imageUrl = (image: ImageResponse) => imgPreview(image.id)

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

async function confirmSearch() {
    await list({ filters: activeSecondary.value, keyword: searchKeyword.value })
}

async function prevPage() {
    if (pageNumber.value <= 1)
        return
    await list({ pageNumber: pageNumber.value - 1, filters: activeSecondary.value, keyword: searchKeyword.value })
    selectedImage.value = null
}

async function nextPage() {
    if (pageNumber.value >= totalPage.value)
        return
    await list({ pageNumber: pageNumber.value + 1, filters: activeSecondary.value, keyword: searchKeyword.value })
    selectedImage.value = null
}

async function jumpToPage(event: Event) {
    const target = event.target as HTMLInputElement
    const value = Number.parseInt(target.value, 10)
    if (!Number.isFinite(value))
        return
    const page = Math.min(Math.max(value, 1), totalPage.value)
    await list({ pageNumber: page, filters: activeSecondary.value, keyword: searchKeyword.value })
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
        searchKeyword.value = ''
        selectedImage.value = null
        activeSecondary.value = []
    }
}, { immediate: true })

watch([activeSecondary], async () => {
    await list({ filters: activeSecondary.value, keyword: searchKeyword.value })
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
                        <div class="flex gap-1 overflow-hidden">
                            <form class="flex overflow-auto gap-1" @submit.prevent>
                                <input
                                    v-for="val in representativeLabels" :key="val" v-model="activeSecondary" type="checkbox"
                                    name="secondary-filter" class="btn" :value="val" :aria-label="val"
                                >
                            </form>
                            <button class="btn btn-square" type="button" @click="activeSecondary = []">
                                x
                            </button>
                        </div>

                        <div class="join w-full">
                            <input
                                v-model="searchKeyword" type="search" class="input input-bordered join-item flex-1"
                                :placeholder="t('search-placeholder')"
                            >
                            <button class="btn btn-neutral join-item" type="button" @click="confirmSearch">
                                {{ t('search') }}
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

                <section class="flex gap-4 items-center justify-between">
                    <div class="text-xs md:text-sm text-base-content/70">
                        {{ t('pagination-status', { page: pageNumber, totalPage, totalRow }) }}
                    </div>
                    <div class="join">
                        <button class="btn btn-sm md:btn-md join-item" type="button" :disabled="pageNumber <= 1" @click="prevPage">
                            {{ t('pagination-prev') }}
                        </button>
                        <input
                            class="input input-bordered join-item input-sm md:input-md w-10 md:w-12 text-center" :value="pageNumber"
                            min="1" :max="totalPage" @change="jumpToPage($event)"
                        >
                        <button
                            class="btn btn-sm md:btn-md join-item" type="button" :disabled="pageNumber >= totalPage"
                            @click="nextPage"
                        >
                            {{ t('pagination-next') }}
                        </button>
                    </div>
                </section>
            </div>

            <div class="modal-action">
                <button class="btn btn-accent" type="button" @click="openUploader = true">
                    {{ t('actions.upload') }}
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
        :suggested-labels="[...activeFilters]" :upload="uploadImage" @update:open="val => openUploader = val"
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
  search: Search
  empty: No images match your filters yet.
  custom-placeholder: Upload your own image
  pagination-status: "Page {page} of {totalPage}, total {total} images"
  pagination-prev: "<"
  pagination-next: ">"
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
  search: 搜索
  empty: 暂无符合条件的图片
  custom-placeholder: 上传你的专属图片
  pagination-status: "第 {page} / {totalPage} 页，共 {totalRow} 张图片"
  pagination-prev: "<"
  pagination-next: ">"
  delete-title: 删除图片
  delete-message: "确定要删除“{name}”吗？"
</i18n>

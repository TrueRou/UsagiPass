<script setup lang="ts">
const props = defineProps<{
    open: boolean
    aspect: ImageAspect
    initialFilters?: string[]
    pageSize?: number
    title?: string
    confirmLabel?: string
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'select', payload: ImageResponse): void
}>()

const { imgPreview } = useUtils()

const {
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
    refresh,
} = useImageList({ aspectId: props.aspect.id, pageSize: props.pageSize, initialFilters: props.initialFilters })

const activeSecondary = ref<string[]>([])
const searchKeyword = ref('')
const selectedImage = ref<ImageResponse | null>(null)
const openUploader = ref(false)
const deleteTarget = ref<ImageResponse | null>(null)
const pending = ref(false)

const title = computed(() => props.title ?? '选择图片')
const confirmButtonText = computed(() => props.confirmLabel ?? '使用此图片')

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

async function handleUploaded(image: ImageResponse) {
    await refresh()
    selectedImage.value = image
}

watch(() => props.open, async (isOpen) => {
    if (isOpen) {
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
        <div class="modal-box max-w-6xl h-[88vh] md:h-[85vh] my-[6vh] md:my-[7.5vh] flex flex-col p-0">
            <!-- 固定头部 -->
            <div class="shrink-0 px-6 pt-6 pb-4 border-b">
                <form method="dialog">
                    <button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4" @click.prevent="close">
                        ✕
                    </button>
                </form>
                <header class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                        <h2 class="text-2xl font-semibold">
                            {{ title }}
                        </h2>
                        <p v-if="aspect" class="text-sm text-base-content/70">
                            比例：{{ aspect.name }} · {{ `${aspect.ratioWidthUnit}:${aspect.ratioHeightUnit}` }}
                        </p>
                    </div>
                </header>
            </div>

            <!-- 可滚动内容区域 -->
            <div class="flex-1 overflow-y-auto px-6 py-6">
                <div class="space-y-6">
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
                                    placeholder="按名称搜索"
                                >
                                <button class="btn btn-neutral join-item" type="button" @click="confirmSearch">
                                    搜索
                                </button>
                            </div>
                        </div>
                    </section>

                    <section class="min-h-80">
                        <div v-if="loading" class="flex items-center justify-center py-16">
                            <span class="loading loading-spinner loading-lg" />
                        </div>
                        <div v-else>
                            <div
                                v-if="images.length === 0"
                                class="rounded-lg border border-dashed p-10 text-center space-y-4"
                            >
                                <p class="text-base-content/60">
                                    暂无符合条件的图片
                                </p>
                                <button class="btn btn-primary" type="button" @click="openUploader = true">
                                    上传新图片
                                </button>
                            </div>
                            <div v-else-if="!aspect">
                                <p>
                                    图片比例加载失败
                                </p>
                            </div>
                            <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                                <ImageCard
                                    v-for="image in images" :key="imageKey(image)" :image="image"
                                    :image-url="imageUrl(image)" :selected="isSelected(image)"
                                    :disabled="pending" :hided-labels="initialFilters"
                                    @select="updateSelection"
                                    @rename="handleRename"
                                    @delete="confirmDelete"
                                />
                            </div>
                        </div>
                    </section>

                    <section class="flex gap-4 items-center justify-between">
                        <div class="text-xs md:text-sm text-base-content/70">
                            第 {{ pageNumber }} / {{ totalPage }} 页，共 {{ totalRow }} 张图片
                        </div>
                        <div class="join">
                            <button class="btn btn-sm md:btn-md join-item" type="button" :disabled="pageNumber <= 1" @click="prevPage">
                                &lt;
                            </button>
                            <input
                                class="input input-bordered join-item input-sm md:input-md w-10 md:w-12 text-center" :value="pageNumber"
                                min="1" :max="totalPage" @change="jumpToPage($event)"
                            >
                            <button
                                class="btn btn-sm md:btn-md join-item" type="button" :disabled="pageNumber >= totalPage"
                                @click="nextPage"
                            >
                                &gt;
                            </button>
                        </div>
                    </section>
                </div>
            </div>

            <!-- 固定底部 -->
            <div class="shrink-0 px-6 pb-6 pt-4 border-t">
                <div class="modal-action mt-0">
                    <button class="btn btn-accent" type="button" @click="openUploader = true">
                        上传新图片
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
        </div>
    </dialog>

    <ImageUploader
        v-if="open" :open="openUploader" :aspect="aspect"
        :suggested-labels="[...activeFilters]" @update:open="val => openUploader = val"
        @uploaded="handleUploaded"
    />

    <dialog v-if="deleteTarget" class="modal modal-open">
        <div class="modal-box">
            <h3 class="font-semibold text-lg mb-4">
                删除图片
            </h3>
            <p>确定要删除“{{ deleteTarget.name }}”吗？</p>
            <div class="modal-action">
                <button class="btn" type="button" @click="deleteTarget = null">
                    取消
                </button>
                <button class="btn btn-error" type="button" :disabled="pending" @click="handleDelete">
                    <span v-if="pending" class="loading loading-spinner" />
                    <span>删除</span>
                </button>
            </div>
        </div>
    </dialog>
</template>

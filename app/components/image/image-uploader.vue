<script setup lang="ts">
import type { VueCropper } from 'vue-cropper'

const props = defineProps<{
    open: boolean
    aspect: ImageAspect
    suggestedLabels?: string[]
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'uploaded', image: ImageResponse): void
}>()

const { $leporid } = useNuxtApp()

const cropper = useTemplateRef<InstanceType<typeof VueCropper>>('cropperRef')
const fileInput = ref<HTMLInputElement | null>(null)
const filePreviewImage = ref<string | null>(null)
const fileRaw = ref<File | null>(null)
const submitting = ref(false)
const tagDraft = ref('')

const metadata = reactive({
    name: '',
    description: '',
    visibility: ImageVisibility.PRIVATE,
    labels: [] as string[],
})

const cropRatio = computed(() => {
    if (props.aspect) {
        return [props.aspect.ratio_width_unit || 1, props.aspect.ratio_height_unit || 1]
    }
    return [4, 3]
})

const cropBox = computed(() => {
    if (!props.aspect) {
        return { width: 300, height: 225 }
    }
    const base = 320
    const total = props.aspect.ratio_width_unit + props.aspect.ratio_height_unit
    const width = (props.aspect.ratio_width_unit / total) * base * 2
    const height = (props.aspect.ratio_height_unit / total) * base * 2
    return { width, height }
})

watch(() => props.open, (value) => {
    if (value) {
        reset()
        nextTick(() => {
            fileInput.value?.focus()
        })
    }
    else {
        cleanupPreview()
    }
})

const canSubmit = computed(() => !!filePreviewImage.value && !!metadata.name.trim() && !submitting.value)

async function handleFileChange(event: Event) {
    const files = (event.target as HTMLInputElement).files
    if (!files || files.length === 0)
        return

    const file = files.item(0)
    if (!file)
        return

    const reader = new FileReader()
    reader.onload = function (ev) {
        filePreviewImage.value = ev.target?.result as string
    }
    reader.readAsDataURL(file)
    fileRaw.value = file
    metadata.name = file.name.replace(/\.[^/.]+$/, '')
    await nextTick()
    cropper.value?.refresh()
}

function rotateLeft() {
    cropper.value?.rotateLeft()
}

function rotateRight() {
    cropper.value?.rotateRight()
}

function resetCrop() {
    cropper.value?.refresh()
}

function addTag() {
    const value = tagDraft.value.trim()
    if (!value)
        return
    if (!metadata.labels.includes(value)) {
        metadata.labels.push(value)
    }
    tagDraft.value = ''
}

function removeTag(label: string) {
    if (label !== 'workshop')
        metadata.labels = metadata.labels.filter(item => item !== label)
}

function close() {
    emit('update:open', false)
}

function cleanupPreview() {
    if (filePreviewImage.value) {
        URL.revokeObjectURL(filePreviewImage.value)
        filePreviewImage.value = null
    }
    fileRaw.value = null
}

function reset() {
    metadata.name = ''
    metadata.description = ''
    metadata.visibility = ImageVisibility.PRIVATE
    metadata.labels = ['workshop', ...props.suggestedLabels ?? []]
    tagDraft.value = ''
    cleanupPreview()
    if (fileInput.value) {
        fileInput.value.value = ''
    }
}

async function submit() {
    if (!canSubmit.value || !filePreviewImage.value || !fileRaw.value)
        return
    submitting.value = true
    try {
        const blob = await new Promise<Blob>((resolve, reject) => {
            cropper.value?.getCropBlob((blob: Blob | null) => {
                if (blob) {
                    resolve(blob)
                }
                else {
                    reject(new Error('Failed to crop image'))
                }
            })
        })

        const formData = new FormData()
        const fileName = fileRaw.value?.name ?? 'image.png'
        formData.append('file', blob, fileName)
        formData.append('aspect_id', props.aspect.id)
        formData.append('name', metadata.name.trim())
        formData.append('description', metadata.description.trim())
        formData.append('visibility', String(metadata.visibility.valueOf()))
        metadata.labels.forEach(label => formData.append('labels', label))

        const response = await $leporid<ImageResponse>('/api/images', {
            method: 'POST',
            body: formData,
        })
        emit('uploaded', response)
        close()
    }
    finally {
        submitting.value = false
    }
}
</script>

<template>
    <dialog v-if="open" class="modal modal-open">
        <div class="modal-box max-w-4xl h-[88vh] md:h-[85vh] my-[6vh] md:my-[7.5vh] flex flex-col p-0">
            <!-- 固定头部 -->
            <div class="shrink-0 px-6 pt-6 pb-4 border-b">
                <form method="dialog">
                    <button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4" @click.prevent="close">
                        ✕
                    </button>
                </form>
                <h3 class="font-bold text-xl flex items-center gap-3">
                    <span>上传图片</span>
                    <span v-if="aspect" class="badge badge-accent">{{ aspect.name }}</span>
                </h3>
            </div>

            <!-- 可滚动内容区域 -->
            <div class="flex-1 overflow-y-auto px-6 py-6">
                <div class="grid gap-8 lg:grid-cols-[2fr,1fr]">
                    <div class="space-y-4">
                        <div class="flex flex-col gap-4">
                            <input
                                ref="fileInput" type="file" accept="image/*"
                                class="file-input file-input-bordered w-full" @change="handleFileChange"
                            >
                            <div
                                v-if="!filePreviewImage"
                                class="p-6 border border-dashed rounded-lg text-center text-base-content/60"
                            >
                                选择一张图片开始裁剪
                            </div>
                            <div v-else class="space-y-3">
                                <ClientOnly>
                                    <div class="rounded-lg border h-64 md:h-80 lg:h-96 w-full overflow-hidden">
                                        <VueCropper
                                            ref="cropper" :img="filePreviewImage" output-type="png" :auto-crop="true" :fixed="true"
                                            :fixed-number="cropRatio" :center-box="false" :auto-crop-width="cropBox.width"
                                            :auto-crop-height="cropBox.height" :full="true" :can-scale="true" :info-true="true"
                                            class="h-64 md:h-80 lg:h-96 w-full"
                                        />
                                    </div>
                                </ClientOnly>
                                <div class="flex flex-wrap gap-2">
                                    <button class="btn btn-sm" type="button" @click="rotateLeft">
                                        ⟲ 向左旋转
                                    </button>
                                    <button class="btn btn-sm" type="button" @click="rotateRight">
                                        ⟳ 向右旋转
                                    </button>
                                    <button class="btn btn-sm" type="button" @click="resetCrop">
                                        重置
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <div>
                            <label class="label">
                                <span class="label-text">名称</span>
                            </label>
                            <input
                                v-model="metadata.name" type="text" class="input input-bordered w-full"
                                placeholder="给图片起个名字"
                            >
                        </div>
                        <div>
                            <label class="label">
                                <span class="label-text">描述</span>
                            </label>
                            <textarea
                                v-model="metadata.description" class="textarea textarea-bordered w-full"
                                placeholder="描述这张图片（可选）" rows="3"
                            />
                        </div>
                        <div>
                            <label class="label">
                                <span class="label-text">可见性</span>
                            </label>
                            <select v-model="metadata.visibility" class="select select-bordered w-full">
                                <option value="PRIVATE">
                                    私有
                                </option>
                                <option value="PUBLIC">
                                    公开
                                </option>
                            </select>
                        </div>
                        <div>
                            <label class="label label-text">标签</label>
                            <div class="flex gap-2 mb-2">
                                <input
                                    v-model="tagDraft" type="text" class="input input-bordered input-sm flex-1"
                                    placeholder="输入标签并按回车" @keyup.enter.prevent="addTag"
                                >
                                <button class="btn btn-sm btn-primary" type="button" @click="addTag">
                                    添加
                                </button>
                            </div>
                            <div class="flex flex-wrap gap-2">
                                <div v-for="label in metadata.labels" :key="label" class="badge badge-lg badge-outline gap-2">
                                    <span>{{ label }}</span>
                                    <button type="button" class="btn btn-xs btn-ghost" @click="removeTag(label)">
                                        ✕
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 固定底部 -->
            <div class="shrink-0 px-6 pb-6 pt-4 border-t">
                <div class="modal-action mt-0">
                    <button class="btn btn-ghost" type="button" @click="close">
                        取消
                    </button>
                    <button class="btn btn-primary" type="button" :disabled="!canSubmit || submitting" @click="submit">
                        <span v-if="submitting" class="loading loading-spinner" />
                        <span>上传</span>
                    </button>
                </div>
            </div>
        </div>
    </dialog>
</template>

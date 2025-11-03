<script setup lang="ts">
import type { VueCropper } from 'vue-cropper'

const props = defineProps<{
    open: boolean
    aspect: ImageAspect | null
    aspectId: string
    suggestedLabels?: string[]
    upload: (formData: FormData) => Promise<{ image: ImageResponse }>
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'uploaded', image: ImageResponse): void
}>()

const { t } = useI18n()

const cropper = useTemplateRef<InstanceType<typeof VueCropper>>('cropperRef')
const fileInput = ref<HTMLInputElement | null>(null)
const filePreviewImage = ref<string | null>(null)
const fileRaw = ref<File | null>(null)
const submitting = ref(false)
const tagDraft = ref('')

const defaultVisibility: ImageVisibility = 'PRIVATE' as ImageVisibility

const metadata = reactive({
    name: '',
    description: '',
    visibility: defaultVisibility,
    labels: [] as string[],
})

const cropRatio = computed(() => {
    if (props.aspect) {
        return [props.aspect.ratioWidthUnit || 1, props.aspect.ratioHeightUnit || 1]
    }
    return [4, 3]
})

const cropBox = computed(() => {
    if (!props.aspect) {
        return { width: 300, height: 225 }
    }
    const base = 320
    const total = props.aspect.ratioWidthUnit + props.aspect.ratioHeightUnit
    const width = (props.aspect.ratioWidthUnit / total) * base * 2
    const height = (props.aspect.ratioHeightUnit / total) * base * 2
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
    metadata.visibility = defaultVisibility
    metadata.labels = props.suggestedLabels ?? []
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
        formData.append('aspect_id', props.aspect?.id ?? props.aspectId)
        formData.append('name', metadata.name.trim())
        if (metadata.description.trim()) {
            formData.append('description', metadata.description.trim())
        }
        formData.append('visibility', metadata.visibility)
        metadata.labels.forEach(label => formData.append('labels', label))

        const result = await props.upload(formData)
        emit('uploaded', result.image)
        close()
    }
    finally {
        submitting.value = false
    }
}
</script>

<template>
    <dialog v-if="open" class="modal modal-open">
        <div class="modal-box max-w-4xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-4 top-4" @click.prevent="close">
                    ✕
                </button>
            </form>
            <h3 class="font-bold text-xl mb-6 flex items-center gap-3">
                <span>{{ t('title') }}</span>
                <span v-if="aspect" class="badge badge-accent">{{ aspect.name }}</span>
            </h3>
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
                            {{ t('placeholder') }}
                        </div>
                        <div v-else class="space-y-3">
                            <ClientOnly>
                                <div class="rounded-lg border h-[320px] w-full overflow-hidden">
                                    <VueCropper
                                        ref="cropper" :img="filePreviewImage" :auto-crop="true" :fixed="true"
                                        :fixed-number="cropRatio" :center-box="true" :auto-crop-width="cropBox.width"
                                        :auto-crop-height="cropBox.height" :full="true" :can-scale="true"
                                        class="h-[320px] w-full"
                                    />
                                </div>
                            </ClientOnly>
                            <div class="flex flex-wrap gap-2">
                                <button class="btn btn-sm" type="button" @click="rotateLeft">
                                    ⟲ {{ t('rotate-left')
                                    }}
                                </button>
                                <button class="btn btn-sm" type="button" @click="rotateRight">
                                    ⟳ {{ t('rotate-right')
                                    }}
                                </button>
                                <button class="btn btn-sm" type="button" @click="resetCrop">
                                    {{ t('reset') }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="label">
                            <span class="label-text">{{ t('name') }}</span>
                        </label>
                        <input
                            v-model="metadata.name" type="text" class="input input-bordered w-full"
                            :placeholder="t('name-placeholder')"
                        >
                    </div>
                    <div>
                        <label class="label">
                            <span class="label-text">{{ t('description') }}</span>
                        </label>
                        <textarea
                            v-model="metadata.description" class="textarea textarea-bordered w-full"
                            :placeholder="t('description-placeholder')" rows="3"
                        />
                    </div>
                    <div>
                        <label class="label">
                            <span class="label-text">{{ t('visibility') }}</span>
                        </label>
                        <select v-model="metadata.visibility" class="select select-bordered w-full">
                            <option value="PRIVATE">
                                {{ t('visibility-private') }}
                            </option>
                            <option value="PUBLIC">
                                {{ t('visibility-public') }}
                            </option>
                        </select>
                    </div>
                    <div>
                        <label class="label label-text">{{ t('labels') }}</label>
                        <div class="flex gap-2 mb-2">
                            <input
                                v-model="tagDraft" type="text" class="input input-bordered input-sm flex-1"
                                :placeholder="t('label-placeholder')" @keyup.enter.prevent="addTag"
                            >
                            <button class="btn btn-sm btn-primary" type="button" @click="addTag">
                                {{ t('add') }}
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
            <div class="modal-action">
                <button class="btn btn-ghost" type="button" @click="close">
                    {{ t('cancel') }}
                </button>
                <button class="btn btn-primary" type="button" :disabled="!canSubmit || submitting" @click="submit">
                    <span v-if="submitting" class="loading loading-spinner" />
                    <span>{{ t('submit') }}</span>
                </button>
            </div>
        </div>
    </dialog>
</template>

<i18n lang="yaml">
en-GB:
  title: Upload image
  placeholder: Choose an image to begin cropping
  rotate-left: Rotate left
  rotate-right: Rotate right
  reset: Reset
  name: Name
  name-placeholder: Give your image a friendly name
  description: Description
  description-placeholder: Describe this image (optional)
  visibility: Visibility
  visibility-private: Private
  visibility-public: Public
  labels: Labels
  label-placeholder: Add a label and press Enter
  add: Add
  cancel: Cancel
  submit: Upload

zh-CN:
  title: 上传图片
  placeholder: 选择一张图片开始裁剪
  rotate-left: 向左旋转
  rotate-right: 向右旋转
  reset: 重置
  name: 名称
  name-placeholder: 给图片起个名字
  description: 描述
  description-placeholder: 描述这张图片（可选）
  visibility: 可见性
  visibility-private: 私有
  visibility-public: 公开
  labels: 标签
  label-placeholder: 输入标签并按回车
  add: 添加
  cancel: 取消
  submit: 上传
</i18n>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
    image: ImageResponse
    hidedLabels?: string[]
    imageUrl: string
    selected: boolean
    disabled?: boolean
}>()

const emit = defineEmits<{
    (event: 'select', image: ImageResponse): void
    (event: 'rename', payload: { image: ImageResponse, name: string }): void
    (event: 'delete', image: ImageResponse): void
}>()

const { t } = useI18n()
const { user } = useUserSession()

const isEditing = ref(false)
const editableName = ref(props.image.name)

watch(() => props.image.name, (name) => {
    if (!isEditing.value) {
        editableName.value = name
    }
})

function canModifyImage(image: ImageResponse) {
    return image.user_id === user.value?.id
}

function handleSelect() {
    if (props.disabled)
        return
    emit('select', props.image)
}

function beginEdit() {
    if (!canModifyImage(props.image)) {
        return
    }
    isEditing.value = true
    editableName.value = props.image.name
}

function submitRename() {
    const trimmed = editableName.value.trim()
    if (!trimmed || trimmed === props.image.name) {
        isEditing.value = false
        editableName.value = props.image.name
        return
    }
    emit('rename', { image: props.image, name: trimmed })
    isEditing.value = false
}

function cancelEdit() {
    editableName.value = props.image.name
    isEditing.value = false
}

function emitDelete() {
    emit('delete', props.image)
}

const representativeLabels = computed(() => {
    return props.image.labels.filter(label => !props.hidedLabels?.includes(label))
})
</script>

<template>
    <div
        class="card bg-base-200 shadow-md hover:shadow-xl transition-shadow cursor-pointer" :class="{
            'ring ring-primary ring-offset-2': selected,
            'opacity-60 pointer-events-none': disabled,
        }" @click="handleSelect"
    >
        <div class="relative">
            <!-- 左上 图片名称 -->
            <div class="absolute top-1 left-1">
                <div v-if="!isEditing" class="badge lg:badge-lg" @click.stop="beginEdit">
                    {{ image.name }}
                </div>
                <div v-else class="flex gap-2 flex-col bg-black/50 p-2 rounded">
                    <input
                        v-model="editableName" type="text" class="input input-xs"
                        :placeholder="t('rename-placeholder')"
                    >
                    <button class="btn btn-xs btn-primary" :disabled="!editableName.trim()" @click.stop="submitRename">
                        {{ t('save') }}
                    </button>
                    <button class="btn btn-xs" @click.stop="cancelEdit">
                        {{ t('cancel') }}
                    </button>
                </div>
            </div>

            <!-- 中间 图片本身 -->
            <div class="w-full overflow-hidden">
                <img :src="imageUrl" :alt="image.name" class="w-full object-cover">
            </div>

            <!-- 右上 选中标记 -->
            <template v-if="selected && !isEditing">
                <div class="absolute top-1 right-1 badge lg:badge-lg badge-primary">
                    {{ t('selected') }}
                </div>
            </template>

            <!-- 右下 操作按钮 -->
            <div v-if="canModifyImage(image)" class="absolute bottom-1 right-1">
                <button class="bg-red-500/80 text-white p-1 rounded-full hover:bg-red-600" @click.stop="emitDelete">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
            </div>

            <!-- 左下 标签 -->
            <div class="absolute bottom-1 left-1 flex flex-col gap-1">
                <span v-for="label in representativeLabels" :key="label" class="badge badge-soft badge-xs sm:badge-sm">
                    {{ label }}
                </span>
            </div>
        </div>
    </div>
</template>

<i18n lang="yaml">
en-GB:
  selected: Selected
  rename: Rename
  delete: Delete
  rename-placeholder: Enter a new name
  save: Save
  cancel: Cancel

zh-CN:
  selected: 已选
  rename: 重命名
  delete: 删除
  rename-placeholder: 输入新名称
  save: 保存
  cancel: 取消
</i18n>

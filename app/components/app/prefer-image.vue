<script setup lang="ts">
import { no } from 'zod/locales'

const props = defineProps<{
    imageId?: string
    label: string
    helper: string
    alt: string
    allowClear?: boolean
}>()

const emit = defineEmits<{
    select: []
    clear: []
}>()

const notificationsStore = useNotificationsStore()

const { img } = useUtils()

function clearImage() {
    if (props.allowClear) {
        emit('clear')
    }
    else {
        notificationsStore.addNotification({
            type: 'warning',
            message: '此图片不允许清空。',
        })
    }
}
</script>

<template>
    <div class="rounded-xl p-4">
        <div class="flex items-start gap-3">
            <div class="flex w-16 items-center justify-center overflow-hidden rounded-lg border border-base-200">
                <img
                    v-if="imageId"
                    :src="img(imageId)"
                    :alt="alt"
                    class="h-full w-full object-cover"
                    loading="lazy"
                >
            </div>
            <div class="flex-1 space-y-1">
                <div class="flex items-center gap-2">
                    <p class="text-sm font-semibold">
                        {{ label }}
                    </p>
                    <slot name="title-action" />
                </div>
                <div class="flex flex-wrap gap-2 pt-1">
                    <button
                        class="btn btn-sm btn-primary"
                        type="button"
                        @click="emit('select')"
                    >
                        {{ imageId ? '更换图片' : '选择图片' }}
                    </button>
                    <button
                        class="btn btn-sm btn-outline btn-error"
                        type="button"
                        @click="clearImage"
                    >
                        清空
                    </button>
                    <slot name="actions" />
                </div>
            </div>
        </div>
    </div>
</template>

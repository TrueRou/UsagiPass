<script setup lang="ts">
const model = defineModel()
const props = defineProps({
    text: String,
    show: Boolean,
    placeholder: {
        type: String,
        default: ''
    }
})
const emits = defineEmits(['confirm', 'cancel'])

// 在确认前聚焦输入框
import { ref, watch } from 'vue'
const inputRef = ref<HTMLInputElement | null>(null)

watch(() => props.show, (newVal) => {
    if (newVal) {
        setTimeout(() => {
            inputRef.value?.focus()
        }, 100)
    }
})

// 键盘事件处理
const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
        emits('confirm')
    } else if (e.key === 'Escape') {
        emits('cancel')
    }
}
</script>

<template>
    <Transition name="prompt-fade">
        <div v-if="props.show" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-30"
            @click.self="emits('cancel')">
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md mx-4 w-full transform transition-all"
                :class="{ 'sm:max-w-lg': true }">
                <div class="p-5 sm:p-6">
                    <h3 class="text-lg sm:text-xl font-medium text-gray-900 dark:text-white mb-3" v-html="props.text">
                    </h3>

                    <input ref="inputRef" v-model="model" type="text" :placeholder="props.placeholder"
                        @keydown="handleKeydown" class="prompt-input">

                    <div class="mt-4 sm:mt-6 flex flex-col sm:flex-row-reverse gap-2 sm:gap-3">
                        <button @click="emits('confirm')" class="prompt-button confirm-button">
                            确定
                        </button>
                        <button @click="emits('cancel')" class="prompt-button cancel-button">
                            取消
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
.prompt-input {
    width: 100%;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 16px;
    line-height: 1.5;
    transition: all 0.2s ease;
    background-color: white;
    color: #1f2937;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.prompt-input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
    outline: none;
}

.dark .prompt-input {
    background-color: #1f2937;
    border-color: #374151;
    color: white;
}

.dark .prompt-input:focus {
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.25);
}

.prompt-button {
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 15px;
    transition: all 0.2s ease;
    flex: 1 1 0;
    text-align: center;
}

.confirm-button {
    background-color: #3b82f6;
    color: white;
}

.confirm-button:hover {
    background-color: #2563eb;
}

.cancel-button {
    background-color: #f3f4f6;
    color: #4b5563;
}

.cancel-button:hover {
    background-color: #e5e7eb;
}

.dark .cancel-button {
    background-color: #374151;
    color: #e5e7eb;
}

.dark .cancel-button:hover {
    background-color: #4b5563;
}

/* 移动端样式优化 */
@media (max-width: 640px) {
    .prompt-button {
        padding: 12px 16px;
    }
}

/* 过渡动画 */
.prompt-fade-enter-active,
.prompt-fade-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.prompt-fade-enter-from,
.prompt-fade-leave-to {
    opacity: 0;
    transform: scale(0.95);
}
</style>
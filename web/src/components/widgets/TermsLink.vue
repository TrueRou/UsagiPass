<script setup lang="ts">
import { onMounted, ref } from 'vue'

defineProps({
    modelValue: {
        type: Boolean,
        default: false
    }
})

const isShaking = ref(false)

const emit = defineEmits<{
    'update:modelValue': [value: boolean]
}>()

const viteDocs = import.meta.env.VITE_DOCS
const STORAGE_KEY = 'usagipass-terms-accepted'

// 组件挂载时从 sessionStorage 读取状态
onMounted(() => {
    const savedState = sessionStorage.getItem(STORAGE_KEY)
    if (savedState === 'true') {
        emit('update:modelValue', true)
    }
})

const updateValue = (event: Event) => {
    const target = event.target as HTMLInputElement
    const checked = target.checked
    
    // 保存状态到 sessionStorage
    sessionStorage.setItem(STORAGE_KEY, checked.toString())
    
    emit('update:modelValue', checked)
}

const shake = () => {
    isShaking.value = true
    setTimeout(() => {
        isShaking.value = false
    }, 600) // 抖动动画持续时间
}

// 暴露shake方法给父组件
defineExpose({
    shake
})
</script>

<template>
    <div 
        class="text-xs text-gray-500 text-center mt-4 flex items-center justify-center gap-2 transition-transform duration-75"
        :class="{ 'animate-pulse shake': isShaking }"
    >
        <input 
            type="checkbox" 
            :checked="modelValue"
            @change="updateValue"
            class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500 focus:ring-2"
            id="terms-checkbox"
        />
        <label for="terms-checkbox" class="cursor-pointer">
            我已阅读并同意
            <a :href="`${viteDocs}/terms-of-use.html`" target="_blank" class="text-blue-500 hover:underline">用户条款</a>
            和
            <a :href="`${viteDocs}/privacy-policy.html`" target="_blank" class="text-blue-500 hover:underline">隐私政策</a>
            的内容。
        </label>
    </div>
</template>

<style scoped>
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.shake {
    animation: shake 0.6s ease-in-out;
}
</style>

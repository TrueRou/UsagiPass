<script setup lang="ts">
defineProps({
    prefix: {
        type: String,
        default: '继续操作即表示您同意'
    }
})

const viteDocs = import.meta.env.VITE_DOCS
</script>

<template>
    <div class="text-xs text-gray-500 text-center mt-2">
        {{ prefix }}
        <a :href="`${viteDocs}/terms-of-use.html`" target="_blank" class="text-blue-500 hover:underline">用户条款</a>
        和
        <a :href="`${viteDocs}/privacy-policy.html`" target="_blank" class="text-blue-500 hover:underline">隐私政策</a>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AdminDrafts from '@/components/admin/AdminDrafts.vue';

const activeTab = ref('drafts');

const tabs = [
    { id: 'drafts', label: '订单管理' },
    { id: 'users', label: '用户管理' },
    { id: 'images', label: '图片管理' }
];
</script>

<template>
    <div class="flex flex-col items-center w-full">
        <!-- 标签页导航 -->
        <div class="flex w-full mt-2 pl-2 pr-2 border-b border-gray-200">
            <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
                class="py-2 px-4 font-medium text-sm focus:outline-none" :class="activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 font-bold'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'">
                {{ tab.label }}
            </button>
        </div>

        <!-- 标签页内容 -->
        <div class="w-full overflow-y-scroll">
            <AdminDrafts v-if="activeTab === 'drafts'" />
            <!-- 其他标签页内容将在这里添加 -->
            <div v-else class="p-4 text-center text-gray-500 h-full">该功能正在开发中...</div>
        </div>
    </div>
</template>

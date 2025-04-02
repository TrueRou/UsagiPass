<script setup lang="ts">
import { ref } from 'vue';
import type { Bests } from '@/types';
import PageBests from './scores/PageBests.vue';
import PageStatistics from './scores/PageStatistics.vue';

defineProps<{
    bests?: Bests
    isLoading?: boolean
}>();

const tabActive = ref('bests');
</script>

<template>
    <div class="w-full h-full absolute top-0 left-0">
        <div class="score-view-container h-full dark:bg-gray-800 dark:text-white">
            <div class="flex border-b dark:border-gray-700">
                <button @click="tabActive = 'bests'"
                    :class="['py-2 px-4', tabActive === 'bests' ? 'border-b-2 border-blue-500 text-blue-500 dark:text-blue-400' : 'dark:text-gray-300']">
                    最佳成绩
                </button>
                <button @click="tabActive = 'statistics'"
                    :class="['py-2 px-4', tabActive === 'statistics' ? 'border-b-2 border-blue-500 text-blue-500 dark:text-blue-400' : 'dark:text-gray-300']">
                    成绩统计
                </button>
            </div>

            <div v-if="isLoading" class="flex justify-center items-center p-10">
                <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 dark:border-blue-400"></div>
            </div>

            <div v-else-if="bests" class="h-[calc(100%-44px)] overflow-y-auto">
                <PageBests v-if="tabActive === 'bests'" :bests="bests" :is-loading="isLoading" />
                <PageStatistics v-else-if="tabActive === 'statistics'" :bests="bests" />
            </div>

            <div v-else class="text-center text-gray-500 dark:text-gray-400 p-10">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="mt-2">无法获取玩家成绩数据</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.score-view-container {
    max-width: 960px;
    margin: 0 auto;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-top: 0.5rem;
}

::-webkit-scrollbar {
    display: none;
}
</style>
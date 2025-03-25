<script setup lang="ts">
import { computed } from 'vue';
import type { Bests } from '@/types';
import ScoreList from './ScoreList.vue';

const props = defineProps<{
    bests: Bests;
}>();

const stats = computed(() => {
    const data = [];

    const total = props.bests.b35_rating + props.bests.b15_rating;
    data.push({
        label: 'BEST 35',
        count: props.bests.b35_rating,
        part: Math.round(props.bests.b35_rating / total * 100),
        color: '#228be6'
    });

    data.push({
        label: 'BEST 15',
        count: props.bests.b15_rating,
        part: Math.round(props.bests.b15_rating / total * 100),
        color: '#fd7e14'
    });

    return data;
});
</script>

<template>
    <div>
        <!-- 评级统计区段 -->
        <div class="bg-white dark:bg-gray-800 mt-4 mb-6 p-3 rounded-md">
            <div class="flex justify-between items-center mb-4">
                <div>
                    <h3 class="text-xl font-bold mb-1 dark:text-white">{{ Math.floor(props.bests.all_rating * 100) / 100
                        }}</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">DX Rating 总和</p>
                </div>
                <div class="animate-spin mr-2 text-gray-700 dark:text-gray-300">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
                <div v-for="(stat, index) in stats" :key="index" class="border-b-2 pb-2"
                    :style="{ borderBottomColor: stat.color }">
                    <div class="text-xs uppercase text-gray-500 dark:text-gray-400 font-bold">
                        {{ stat.label }}
                    </div>

                    <div class="flex justify-between items-end">
                        <div class="font-bold dark:text-white">{{ stat.count }}</div>
                        <div class="text-sm font-bold" :style="{ color: stat.color }">
                            {{ stat.part }}%
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- B35成绩展示 -->
        <div v-if="'b35_scores' in bests && bests.b35_scores.length" class="mb-6">
            <h3 class="text-xl font-bold mb-1 dark:text-white">Best 35</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">旧版本最佳曲目</p>
            <ScoreList :scores="bests.b35_scores" />
        </div>

        <!-- B15成绩展示 -->
        <div v-if="'b15_scores' in bests && bests.b15_scores.length" class="mb-6">
            <h3 class="text-xl font-bold mb-1 dark:text-white">Best 15</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">现版本最佳曲目</p>
            <ScoreList :scores="bests.b15_scores" />
        </div>
    </div>
</template>

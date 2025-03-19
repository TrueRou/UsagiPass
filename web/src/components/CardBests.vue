<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import type { CardBests } from '@/types';
import ScoreBestsSection from '@/components/scores/ScoreBests.vue';
import ScoreStatisticsSection from '@/components/scores/ScoreStatistics.vue';

const userStore = useUserStore();


const cardUuid = ref(history.state.uuid || '');
const bests = ref<CardBests | null>(null);
const loading = ref(true);
const tabActive = ref('bests'); // 可选择bests或statistics

onMounted(async () => {
    if (cardUuid.value) {
        await fetchCardBests();
    }
});

async function fetchCardBests() {
    loading.value = true;

    try {
        const response = await userStore.axiosInstance.get(`/cards/${cardUuid.value}/bests`);
        bests.value = response.data;
    } catch (error) {
        console.log("Card has no bests data, skipped");
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="w-full overflow-y-scroll">
        <div class="score-view-container">
            <div class="flex border-b mb-4">
                <button @click="tabActive = 'bests'"
                    :class="['py-2 px-4', tabActive === 'bests' ? 'border-b-2 border-blue-500 text-blue-500' : '']">
                    最佳成绩
                </button>
                <button @click="tabActive = 'statistics'"
                    :class="['py-2 px-4', tabActive === 'statistics' ? 'border-b-2 border-blue-500 text-blue-500' : '']">
                    成绩统计
                </button>
            </div>

            <div v-if="loading" class="flex justify-center items-center p-10">
                <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
            </div>

            <div v-else-if="!bests" class="text-center text-gray-500 p-10">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="mt-2">无法获取玩家成绩数据</p>
            </div>

            <div v-else>
                <ScoreBestsSection v-if="tabActive === 'bests'" :bests="bests" />
                <ScoreStatisticsSection v-else-if="tabActive === 'statistics'" :bests="bests" />
            </div>
        </div>
    </div>
</template>

<style scoped>
.score-view-container {
    max-width: 960px;
    margin: 0 auto;
    padding: 1rem;
}
</style>

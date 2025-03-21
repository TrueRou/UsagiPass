<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Score } from '@/types';
import ScoreCard from './ScoreCard.vue';

const props = defineProps<{
    scores: Score[];
}>();

const selectedScore = ref<Score | null>(null);
const showScoreDetail = ref(false);

// 打开成绩详情
function openScoreDetail(score: Score) {
    selectedScore.value = score;
    showScoreDetail.value = true;
}

// 关闭成绩详情
function closeScoreDetail() {
    showScoreDetail.value = false;
}

// 根据屏幕大小设置每行显示的卡片数量
const gridClass = computed(() => {
    return 'grid grid-cols-1 sm:grid-cols-2 gap-2';
});
</script>

<template>
    <div>
        <!-- 成绩列表 -->
        <div :class="gridClass">
            <ScoreCard v-for="score in scores" :key="`${score.song_id}:${score.type}:${score.level_index}`"
                :score="score" @click="openScoreDetail(score)" />
        </div>

        <!-- 成绩详情弹窗 -->
        <Teleport to="body">
            <div v-if="showScoreDetail && selectedScore"
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000] p-4">
                <div class="bg-white dark:bg-gray-800 rounded-lg max-w-lg w-full max-h-[90vh] overflow-auto">
                    <div class="p-4 bg-blue-400 text-white flex justify-between items-center">
                        <span class="font-bold">成绩详情</span>
                        <button @click="closeScoreDetail" class="text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                    <div class="p-4">
                        <div class="mb-4">
                            <h3 class="font-bold">{{ selectedScore.song_name }}</h3>
                            <p class="text-sm text-gray-500">难度: {{ selectedScore.level }}</p>
                        </div>

                        <div class="grid grid-cols-2 gap-4">
                            <div class="border rounded p-2">
                                <p class="text-xs text-gray-500">达成率</p>
                                <p class="font-bold">
                                    {{ selectedScore.achievements ? parseInt(String(selectedScore.achievements)) : '-'
                                    }}
                                    <span v-if="selectedScore.achievements" class="text-sm">
                                        .{{ (String(selectedScore.achievements).split(".")[1] || "0").padEnd(4, "0") }}%
                                    </span>
                                </p>
                            </div>

                            <div class="border rounded p-2">
                                <p class="text-xs text-gray-500">DX Rating</p>
                                <p class="font-bold">{{ selectedScore.dx_rating || '-' }}</p>
                            </div>

                            <div class="border rounded p-2">
                                <p class="text-xs text-gray-500">完美连击</p>
                                <p class="font-bold">{{ selectedScore.fc || '无' }}</p>
                            </div>

                            <div class="border rounded p-2">
                                <p class="text-xs text-gray-500">同步率</p>
                                <p class="font-bold">{{ selectedScore.fs || '无' }}</p>
                            </div>

                            <div class="border rounded p-2 col-span-2">
                                <p class="text-xs text-gray-500">最后游玩时间</p>
                                <p class="font-bold">{{ new Date(selectedScore.updated_at).toLocaleString() }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

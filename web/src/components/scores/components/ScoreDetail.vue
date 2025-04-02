<script setup lang="ts">
import type { Score } from '@/types';
import { getFCText, getFSText } from '@/utils/scoreUtils';

defineProps<{
    score: Score | null;
    show: boolean;
}>();

const emit = defineEmits<{
    (e: 'close'): void;
}>();

function closeDetail() {
    emit('close');
}
</script>

<template>
    <Teleport to="body">
        <div v-if="show && score"
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000] p-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg max-w-lg w-full max-h-[90vh] overflow-auto">
                <div class="p-4 bg-blue-400 dark:bg-blue-600 text-white flex justify-between items-center">
                    <span class="font-bold">成绩详情</span>
                    <button @click="closeDetail" class="text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
                <div class="p-4">
                    <div class="mb-4 flex items-start">
                        <img :src="`https://assets2.lxns.net/maimai/jacket/${score.song_id}.png`"
                            class="w-16 h-16 mr-3 rounded object-cover" alt="歌曲封面" />
                        <div>
                            <h3 class="font-bold dark:text-white">{{ score.song_name }}</h3>
                            <p class="text-sm text-gray-500 dark:text-gray-400">难度: {{ score.level }}</p>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div class="border rounded p-2 dark:border-gray-700 dark:bg-gray-700">
                            <p class="text-xs text-gray-500 dark:text-gray-300">达成率</p>
                            <p class="font-bold dark:text-white">
                                {{ score.achievements ? parseInt(String(score.achievements)) : '-' }}
                                <span v-if="score.achievements" class="text-sm">
                                    .{{ (String(score.achievements).split(".")[1] || "0").padEnd(4, "0") }}%
                                </span>
                            </p>
                        </div>

                        <div class="border rounded p-2 dark:border-gray-700 dark:bg-gray-700">
                            <p class="text-xs text-gray-500 dark:text-gray-300">DX Rating</p>
                            <p class="font-bold dark:text-white">{{ score.dx_rating || '-' }}</p>
                        </div>

                        <div class="border rounded p-2 dark:border-gray-700 dark:bg-gray-700">
                            <p class="text-xs text-gray-500 dark:text-gray-300">连击评价</p>
                            <div class="flex items-center h-8">
                                <p class="font-bold dark:text-white">{{ getFCText(score.fc) }}</p>
                            </div>
                        </div>

                        <div class="border rounded p-2 dark:border-gray-700 dark:bg-gray-700">
                            <p class="text-xs text-gray-500 dark:text-gray-300">同步评价</p>
                            <div class="flex items-center h-8">
                                <p class="font-bold dark:text-white">{{ getFSText(score.fs) }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

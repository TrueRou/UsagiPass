<script setup lang="ts">
import { computed } from 'vue';
import type { Score } from '@/types';

const props = defineProps<{
    score: Score;
}>();

// 获取成绩卡片背景颜色
const cardBackgroundColor = computed(() => {
    const difficultyColors = {
        0: '#6fe163', // BASIC
        1: '#ffd653', // ADVANCED
        2: '#ff7b7b', // EXPERT
        3: '#9f51dc', // MASTER
        4: '#dbaaff', // Re:MASTER
    };

    const levelIndex = props.score.level_index;
    return difficultyColors[levelIndex] || '#26c9fc';
});

// 获取成绩牌子标志
const achievementBadge = computed(() => {
    if (!props.score.achievements) return null;

    const achievements = props.score.achievements;
    if (achievements >= 100.5) return { name: 'SSS+', color: 'bg-purple-600' };
    if (achievements >= 100) return { name: 'SSS', color: 'bg-purple-500' };
    if (achievements >= 99.5) return { name: 'SS+', color: 'bg-yellow-500' };
    if (achievements >= 99) return { name: 'SS', color: 'bg-yellow-400' };
    if (achievements >= 98) return { name: 'S+', color: 'bg-green-600' };
    if (achievements >= 97) return { name: 'S', color: 'bg-green-500' };
    if (achievements >= 94) return { name: 'AAA', color: 'bg-blue-600' };
    if (achievements >= 90) return { name: 'AA', color: 'bg-blue-500' };
    if (achievements >= 80) return { name: 'A', color: 'bg-blue-400' };
    return { name: 'B', color: 'bg-gray-500' };
});

// 获取歌曲类型标签
const songTypeLabel = computed(() => {
    const types = {
        'standard': { name: 'SD', color: 'bg-blue-500' },
        'dx': { name: 'DX', color: 'bg-orange-500' },
        'utage': { name: 'UT', color: 'bg-red-800' }
    };

    return types[props.score.type] || { name: '标准', color: 'bg-blue-500' };
});
</script>

<template>
    <div class="relative overflow-hidden bg-white dark:bg-gray-800 border-2 rounded-md shadow-sm hover:shadow-md transition-shadow cursor-pointer h-20"
        :style="{ borderColor: cardBackgroundColor }" @click="$emit('click')">

        <!-- 背景图片(假设) -->
        <div class="absolute inset-0 opacity-25" :style="{ backgroundColor: cardBackgroundColor }"></div>

        <div class="relative p-2 flex items-center h-full">
            <!-- 左侧信息 -->
            <div class="flex-1 min-w-0 mr-2">
                <!-- 歌曲类型标签 -->
                <span class="inline-block text-xs text-white px-1 py-0.5 rounded mr-1" :class="songTypeLabel.color">
                    {{ songTypeLabel.name }}
                </span>

                <!-- 歌曲名称 (使用truncate确保不会超出) -->
                <div class="font-bold text-sm truncate max-w-full">{{ props.score.song_name }}</div>

                <!-- 达成率和DX评分 -->
                <div v-if="props.score.achievements" class="text-sm">
                    <span class="font-bold">
                        {{ parseInt(String(props.score.achievements)) }}
                        <span class="text-xs">.{{ (String(props.score.achievements).split(".")[1] || "0").padEnd(4, "0")
                            }}%</span>
                    </span>
                    <span class="text-xs text-gray-500 ml-1">DX: {{ props.score.dx_rating }}</span>
                </div>
                <div v-else class="text-sm text-gray-500">未游玩</div>
            </div>

            <!-- 右侧等级和评级 -->
            <div class="flex flex-col items-center justify-center flex-shrink-0">
                <!-- 难度等级 -->
                <div class="w-8 h-8 flex items-center justify-center rounded-md border border-gray-300"
                    :style="{ backgroundColor: cardBackgroundColor, color: 'white' }">
                    {{ props.score.level }}
                </div>

                <!-- 成绩评级标志 -->
                <div v-if="achievementBadge" class="text-xs text-white px-1 rounded mt-1"
                    :class="achievementBadge.color">
                    {{ achievementBadge.name }}
                </div>
            </div>
        </div>
    </div>
</template>

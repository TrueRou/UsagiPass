<script setup lang="ts">
import { computed } from 'vue';
import type { Score } from '@/types';
import { getDifficultyColor, getAchievementStyle, getSongTypeLabel, getFCIconSrc, getFSIconSrc, getSongJacketUrl, getAchievementIconSrc } from '@/utils/scoreUtils';

const props = defineProps<{
    score: Score;
}>();

const cardBackgroundColor = computed(() => {
    return getDifficultyColor(props.score.level_index);
});

const songJacketUrl = computed(() => {
    return getSongJacketUrl(props.score.song_id);
});

const achievementBadge = computed(() => {
    if (!props.score.achievements) return null;
    const style = getAchievementStyle(props.score.achievements);
    return { name: style.name, color: style.color };
});

const achievementIconSrc = computed(() => {
    return getAchievementIconSrc(props.score.achievements);
});

const songTypeLabel = computed(() => {
    return getSongTypeLabel(props.score.type);
});
</script>

<template>
    <div class="relative overflow-hidden bg-white dark:bg-gray-800 border-2 rounded-md shadow-sm hover:shadow-md transition-shadow cursor-pointer h-20"
        :style="{ borderColor: cardBackgroundColor }" @click="$emit('click')">

        <!-- 背景图片 -->
        <div class="absolute inset-0 opacity-25 dark:opacity-15">
            <img v-if="songJacketUrl" :src="songJacketUrl" alt="歌曲封面" class="w-full h-full object-cover" />
            <div v-show="!songJacketUrl" class="w-full h-full" :style="{ backgroundColor: cardBackgroundColor }"></div>
        </div>

        <div class="relative p-2 flex items-center h-full">
            <!-- 歌曲封面 -->
            <div
                class="w-14 h-14 flex-shrink-0 rounded-sm border border-gray-300 dark:border-gray-600 overflow-hidden mr-2">
                <img v-if="songJacketUrl" :src="songJacketUrl" alt="歌曲封面" class="w-full h-full object-cover" />
                <div v-show="!songJacketUrl" class="w-full h-full" :style="{ backgroundColor: cardBackgroundColor }">
                </div>
            </div>

            <!-- 左侧信息 -->
            <div class="flex-1 min-w-0 mr-2">
                <!-- 歌曲类型标签 -->
                <span class="inline-block text-xs text-white px-1 py-0.5 rounded mr-1" :class="songTypeLabel.color">
                    {{ songTypeLabel.name }}
                </span>

                <!-- 歌曲名称 -->
                <div class="font-bold text-sm truncate max-w-full dark:text-white">{{ props.score.song_name }}</div>

                <!-- 达成率和DX评分 -->
                <div v-if="props.score.achievements" class="text-sm mt-1">
                    <span class="font-bold dark:text-white">
                        {{ parseInt(String(props.score.achievements)) }}
                        <span class="text-xs">.{{ (String(props.score.achievements).split(".")[1] || "0").padEnd(4, "0")
                            }}%</span>
                    </span>
                    <span class="text-xs text-gray-500 dark:text-gray-400 ml-1">DX: {{ props.score.dx_rating }}</span>
                </div>
                <div v-else class="text-sm text-gray-500 dark:text-gray-400 mt-1">未游玩</div>
            </div>

            <!-- 右侧等级和评级 -->
            <div class="flex items-center justify-center flex-shrink-0">
                <div class="flex mr-2">
                    <!-- 成绩评级图标 -->
                    <div v-if="achievementIconSrc" class="flex items-center justify-center">
                        <img :src="achievementIconSrc" alt="评级" class="h-10 w-auto" />
                    </div>
                    <div v-else-if="achievementBadge" class="text-xs text-white px-1 rounded"
                        :class="achievementBadge.color">
                        {{ achievementBadge.name }}
                    </div>
                </div>
                <div class="flex-col">
                    <!-- 难度等级 -->
                    <div class="w-auto h-8 flex items-center justify-center rounded-md border border-gray-300 dark:border-gray-600"
                        :style="{ backgroundColor: cardBackgroundColor, color: 'white' }">
                        {{ props.score.level_value.toFixed(1) }}
                    </div>

                    <!-- FC/FS 图标显示 -->
                    <div class="flex items-center">
                        <div class="flex items-center w-6 h-6 justify-center">
                            <img v-if="getFCIconSrc(props.score.fc)" :src="getFCIconSrc(props.score.fc)" alt="FC Status"
                                class="h-6 w-6" />
                        </div>
                        <div class="flex items-center w-6 h-6 justify-center">
                            <img v-if="getFSIconSrc(props.score.fs)" :src="getFSIconSrc(props.score.fs)" alt="FS Status"
                                class="h-6 w-6" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

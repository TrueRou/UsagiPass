<script setup lang="ts">
import { computed } from 'vue';
import type { Score, FCType, FSType } from '@/types';
import { TileDisplayMode, FCTypeMap, FSTypeMap } from '@/types';

const props = defineProps<{
    scores: Score[];
    displayMode?: TileDisplayMode;
}>();

// 获取成绩难度颜色
function getDifficultyColor(levelIndex: number): string {
    const colors: { [key: number]: string } = {
        0: '#6fe163', // BASIC
        1: '#ffd653', // ADVANCED
        2: '#ff7b7b', // EXPERT
        3: '#9f51dc', // MASTER
        4: '#dbaaff', // Re:MASTER
    };
    return colors[levelIndex] || '#26c9fc';
}

// 获取成绩评级样式
function getAchievementStyle(achievements: number | null) {
    if (!achievements) return { class: 'bg-gray-500', text: '-' };

    if (achievements >= 100.5) return { class: 'bg-purple-600', text: 'SSS+' };
    if (achievements >= 100) return { class: 'bg-purple-500', text: 'SSS' };
    if (achievements >= 99.5) return { class: 'bg-yellow-500', text: 'SS+' };
    if (achievements >= 99) return { class: 'bg-yellow-400', text: 'SS' };
    if (achievements >= 98) return { class: 'bg-green-600', text: 'S+' };
    if (achievements >= 97) return { class: 'bg-green-500', text: 'S' };
    return { class: 'bg-blue-500', text: 'A' };
}

// 处理封面图加载错误
function handleImageError(event: Event) {
    const target = event.target as HTMLImageElement;
    target.src = 'https://via.placeholder.com/80?text=No+Image';
}

// 获取当前显示模式
const currentDisplayMode = computed(() => props.displayMode || TileDisplayMode.RATING);

// 特定曲目的查询参数
const gridClass = computed(() => {
    return 'grid grid-cols-5 gap-2';
});

// 将FC状态转换为显示文本
const getFCText = (fc: FCType | null) => {
    if (fc === null) return 'NO FC';
    return FCTypeMap[fc as FCType] || 'NO FC';
};

// 将FS状态转换为显示文本
const getFSText = (fs: FSType | null) => {
    if (fs === null) return 'NO FS';
    return FSTypeMap[fs as FSType] || 'NO FS';
};

// 获取显示内容
function getDisplayContent(score: Score) {
    switch (currentDisplayMode.value) {
        case TileDisplayMode.RATING:
            return getAchievementStyle(score.achievements).text;
        case TileDisplayMode.ACHIEVEMENT:
            return score.achievements ? `${score.achievements}%` : '-';
        case TileDisplayMode.FC:
            return getFCText(score.fc);
        case TileDisplayMode.FS:
            return getFSText(score.fs);
        case TileDisplayMode.DX_RATING:
            return `DX ${score.dx_rating || 0}`;
        default:
            return '';
    }
}

// 获取显示样式
function getDisplayClass(score: Score) {
    switch (currentDisplayMode.value) {
        case TileDisplayMode.RATING:
            return getAchievementStyle(score.achievements).class;
        case TileDisplayMode.ACHIEVEMENT:
            return 'bg-blue-600';
        case TileDisplayMode.FC:
            return score.fc ? 'bg-green-600' : 'bg-gray-600';
        case TileDisplayMode.FS:
            return score.fs ? 'bg-indigo-600' : 'bg-gray-600';
        case TileDisplayMode.DX_RATING:
            return 'bg-yellow-600';
        default:
            return 'bg-gray-600';
    }
}
</script>

<template>
    <div :class="gridClass">
        <div v-for="score in scores" :key="`${score.song_id}:${score.type}:${score.level_index}`"
            class="relative group cursor-pointer rounded overflow-hidden shadow-sm hover:shadow-md transition-shadow"
            @click="$emit('score-click', score)">

            <!-- 歌曲封面 -->
            <div class="aspect-square overflow-hidden">
                <img :src="`https://assets2.lxns.net/maimai/jacket/${score.song_id}.png`" @error="handleImageError"
                    class="w-full h-full object-cover transition-transform group-hover:scale-110"
                    :alt="score.song_name">
            </div>

            <!-- 难度指示条 -->
            <div class="absolute top-0 left-0 right-0 h-1"
                :style="{ backgroundColor: getDifficultyColor(score.level_index) }"></div>

            <!-- 显示内容 -->
            <div class="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
                <div class="text-white text-base font-bold px-2 py-1 rounded text-center"
                    :class="getDisplayClass(score)">
                    {{ getDisplayContent(score) }}
                </div>
            </div>

            <!-- 歌曲名称 (始终在底部显示) -->
            <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 p-1">
                <div class="text-white text-xs font-bold truncate">
                    {{ score.song_name }}
                </div>
            </div>
        </div>
    </div>
</template>

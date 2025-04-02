<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Score } from '@/types';
import { ViewMode, TileDisplayMode } from '@/types';
import ScoreDetail from './ScoreDetail.vue';
import ScoreCardView from '../viewport/ScoreCardView.vue';
import ScoreTileView from '../viewport/ScoreTileView.vue';

const props = defineProps<{
    scores: Score[];
    viewMode?: ViewMode;
    displayMode?: TileDisplayMode;
}>();

const emit = defineEmits<{
    (e: 'toggle-display-mode', mode: TileDisplayMode): void;
}>();

const selectedScore = ref<Score | null>(null);
const showScoreDetail = ref(false);

function openScoreDetail(score: Score) {
    selectedScore.value = score;
    showScoreDetail.value = true;
}

function closeScoreDetail() {
    showScoreDetail.value = false;
}

const currentViewMode = computed(() => props.viewMode || ViewMode.LIST);

const displayModeOptions = [
    { value: TileDisplayMode.RATING, label: '评级', icon: 'star' },
    { value: TileDisplayMode.ACHIEVEMENT, label: '达成率', icon: 'percentage' },
    { value: TileDisplayMode.FC, label: '连击', icon: 'fire' },
    { value: TileDisplayMode.FS, label: '同步', icon: 'music' },
    { value: TileDisplayMode.DX_RATING, label: 'DX分数', icon: 'chart-bar' },
    { value: TileDisplayMode.LEVEL_VALUE, label: '定数', icon: 'hashtag' },
    { value: TileDisplayMode.NONE, label: '无', icon: 'image' },
];

function setTileDisplayMode(mode: TileDisplayMode) {
    emit('toggle-display-mode', mode);
}
</script>

<template>
    <div>
        <!-- 平铺视图的显示模式选择器 -->
        <div v-if="currentViewMode === ViewMode.TILE" class="mb-3 flex flex-wrap gap-2">
            <button v-for="option in displayModeOptions" :key="option.value"
                @click="setTileDisplayMode(option.value as TileDisplayMode)"
                class="px-3 py-1.5 text-sm rounded-md transition-colors"
                :class="displayMode === option.value ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700 dark:text-gray-300'">
                {{ option.label }}
            </button>
        </div>

        <!-- 列表视图 -->
        <div v-if="currentViewMode === ViewMode.LIST" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <ScoreCardView v-for="score in scores" :key="`${score.song_id}:${score.type}:${score.level_index}`"
                :score="score" @click="openScoreDetail(score)" />
        </div>

        <!-- 平铺视图 -->
        <div v-else-if="currentViewMode === ViewMode.TILE">
            <ScoreTileView :scores="scores" :display-mode="displayMode" @score-click="openScoreDetail" />
        </div>

        <!-- 成绩详情组件 -->
        <ScoreDetail :score="selectedScore" :show="showScoreDetail" @close="closeScoreDetail" />
    </div>
</template>

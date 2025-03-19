<script setup lang="ts">
import { computed } from 'vue';
import type { CardBests } from '@/types';

const props = defineProps<{
    bests: CardBests;
}>();

const allScores = computed(() => {
    const scores = [];

    if ('b15_scores' in props.bests) {
        scores.push(...props.bests.b15_scores);
    }
    if ('b35_scores' in props.bests) {
        scores.push(...props.bests.b35_scores);
    }

    return scores;
});

// 计算成绩等级分布
const achievementDistribution = computed(() => {
    const distribution = {
        'SSS+': 0,
        'SSS': 0,
        'SS+': 0,
        'SS': 0,
        'S+': 0,
    };

    allScores.value.forEach(score => {
        if (!score.achievements) return;

        const achievements = score.achievements;
        if (achievements >= 100.5) distribution['SSS+']++;
        else if (achievements >= 100) distribution['SSS']++;
        else if (achievements >= 99.5) distribution['SS+']++;
        else if (achievements >= 99) distribution['SS']++;
        else if (achievements >= 98) distribution['S+']++;
    });

    return distribution;
});

// 计算曲目类型分布
const songTypeDistribution = computed(() => {
    const distribution = {
        'STANDARD': 0,
        'DX': 0,
        'UTAGE': 0
    };

    allScores.value.forEach(score => {
        if (score.type === 'standard') distribution['STANDARD']++;
        else if (score.type === 'dx') distribution['DX']++;
        else if (score.type === 'utage') distribution['UTAGE']++;
    });

    return distribution;
});

// 计算难度系数分布
const levelDistribution = computed(() => {
    // 初始化分布对象
    const distribution: Record<string, number> = {};

    // 统计每个难度的数量
    allScores.value.forEach(score => {
        if (!score.level) return;

        const levelKey = score.level.toString();
        if (distribution[levelKey] === undefined) {
            distribution[levelKey] = 1;
        } else {
            distribution[levelKey]++;
        }
    });

    // 获取有数据的难度区间
    const nonEmptyLevels = Object.keys(distribution).map(Number).sort((a, b) => b - a);

    // 如果没有数据，返回空对象
    if (nonEmptyLevels.length === 0) return {};

    return Object.fromEntries(
        Object.entries(distribution).sort((a, b) => Number(b[0]) - Number(a[0]))
    );


});

// 计算最高和平均达成率
const achievementStats = computed(() => {
    let sum = 0;
    let count = 0;
    let max = 0;

    allScores.value.forEach(score => {
        if (!score.achievements) return;

        sum += score.achievements;
        count++;
        if (score.achievements > max) max = score.achievements;
    });

    return {
        average: count > 0 ? Math.round((sum / count) * 100) / 100 : 0,
        max: Math.round(max * 100) / 100
    };
});
</script>

<template>
    <div>
        <!-- 总体统计 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md p-4 mb-4">
            <div class="mb-2">
                <h3 class="text-lg font-bold">总体统计</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div class="border rounded p-3">
                    <div class="text-sm text-gray-500 dark:text-gray-400">DX Rating</div>
                    <div class="text-xl font-bold" v-if="'all_rating' in bests">{{ bests.all_rating }}</div>
                    <div class="text-xl font-bold" v-else>-</div>
                </div>
                <div class="border rounded p-3">
                    <div class="text-sm text-gray-500 dark:text-gray-400">最高达成率</div>
                    <div class="text-xl font-bold">{{ achievementStats.max }}%</div>
                </div>
                <div class="border rounded p-3">
                    <div class="text-sm text-gray-500 dark:text-gray-400">平均达成率</div>
                    <div class="text-xl font-bold">{{ achievementStats.average }}%</div>
                </div>
            </div>
        </div>

        <!-- 成绩等级分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md p-4 mb-4">
            <div class="mb-2">
                <h3 class="text-lg font-bold">成绩等级分布</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
                <div class="border rounded p-2 text-center bg-purple-600 text-white">
                    <div class="font-bold">SSS+</div>
                    <div>{{ achievementDistribution['SSS+'] }}</div>
                </div>
                <div class="border rounded p-2 text-center bg-purple-500 text-white">
                    <div class="font-bold">SSS</div>
                    <div>{{ achievementDistribution['SSS'] }}</div>
                </div>
                <div class="border rounded p-2 text-center bg-yellow-500 text-white">
                    <div class="font-bold">SS+</div>
                    <div>{{ achievementDistribution['SS+'] }}</div>
                </div>
                <div class="border rounded p-2 text-center bg-yellow-400 text-white">
                    <div class="font-bold">SS</div>
                    <div>{{ achievementDistribution['SS'] }}</div>
                </div>
                <div class="border rounded p-2 text-center bg-green-600 text-white">
                    <div class="font-bold">S+</div>
                    <div>{{ achievementDistribution['S+'] }}</div>
                </div>
            </div>
        </div>

        <!-- 曲目类型分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md p-4 mb-4">
            <div class="mb-2">
                <h3 class="text-lg font-bold">曲目类型分布</h3>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div class="border rounded p-2 flex justify-between items-center bg-blue-500 text-white">
                    <div class="font-bold">标准</div>
                    <div>{{ songTypeDistribution['STANDARD'] }}</div>
                </div>
                <div class="border rounded p-2 flex justify-between items-center bg-orange-500 text-white">
                    <div class="font-bold">DX</div>
                    <div>{{ songTypeDistribution['DX'] }}</div>
                </div>
            </div>
        </div>

        <!-- 难度系数分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md p-4 mb-4">
            <div class="mb-2">
                <h3 class="text-lg font-bold">难度系数分布</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div v-for="(count, level) in levelDistribution" :key="level"
                    class="border rounded p-2 flex justify-between items-center" :class="{
                        'bg-purple-900 text-white': String(level).includes('15'),
                        'bg-purple-700 text-white': String(level).includes('14'),
                        'bg-purple-500 text-white': String(level).includes('13'),
                        'bg-indigo-600 text-white': String(level).includes('12'),
                        'bg-blue-600 text-white': String(level).includes('11'),
                        'bg-teal-600 text-white': String(level).includes('10'),
                        'bg-green-700 text-white': String(level).includes('9'),
                        'bg-green-600 text-white': String(level).includes('8'),
                        'bg-green-500 text-white': parseInt(String(level)) < 8
                    }">
                    <div class="font-bold">{{ level }}</div>
                    <div>{{ count }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 可以添加一些额外的样式 */
</style>

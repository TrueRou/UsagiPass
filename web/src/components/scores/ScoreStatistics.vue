<script setup lang="ts">
import { computed } from 'vue';
import type { Bests } from '@/types';

const props = defineProps<{
    bests: Bests;
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
        average: count > 0 ? (sum / count) : 0,
        max: max
    };
});
</script>

<template>
    <div class="pl-1 pr-1 mt-4">
        <!-- 总体统计 -->
        <div class="bg-white dark:bg-gray-800 rounded-md mb-4 p-3">
            <div class="mb-2">
                <h3 class="text-lg font-bold dark:text-gray-200">总体统计</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div class="border dark:border-gray-700 rounded p-3 dark:bg-gray-700">
                    <div class="text-sm text-gray-500 dark:text-gray-300">DX Rating</div>
                    <div class="text-xl font-bold dark:text-white" v-if="'all_rating' in bests">{{ bests.all_rating }}
                    </div>
                    <div class="text-xl font-bold dark:text-white" v-else>-</div>
                </div>
                <div class="border dark:border-gray-700 rounded p-3 dark:bg-gray-700">
                    <div class="text-sm text-gray-500 dark:text-gray-300">最高达成率</div>
                    <div class="text-xl font-bold dark:text-white">{{ achievementStats.max.toFixed(4) }}%</div>
                </div>
                <div class="border dark:border-gray-700 rounded p-3 dark:bg-gray-700">
                    <div class="text-sm text-gray-500 dark:text-gray-300">平均达成率</div>
                    <div class="text-xl font-bold dark:text-white">{{ achievementStats.average.toFixed(4) }}%</div>
                </div>
            </div>
        </div>

        <!-- 成绩等级分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md mb-4 p-3">
            <div class="mb-2">
                <h3 class="text-lg font-bold dark:text-gray-200">成绩等级分布</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
                <div
                    class="border rounded p-2 text-center bg-purple-600 text-white dark:bg-purple-700 dark:border-purple-800">
                    <div class="font-bold">SSS+</div>
                    <div>{{ achievementDistribution['SSS+'] }}</div>
                </div>
                <div
                    class="border rounded p-2 text-center bg-purple-500 text-white dark:bg-purple-600 dark:border-purple-700">
                    <div class="font-bold">SSS</div>
                    <div>{{ achievementDistribution['SSS'] }}</div>
                </div>
                <div
                    class="border rounded p-2 text-center bg-yellow-500 text-white dark:bg-yellow-600 dark:border-yellow-700">
                    <div class="font-bold">SS+</div>
                    <div>{{ achievementDistribution['SS+'] }}</div>
                </div>
                <div
                    class="border rounded p-2 text-center bg-yellow-400 text-white dark:bg-yellow-500 dark:border-yellow-600">
                    <div class="font-bold">SS</div>
                    <div>{{ achievementDistribution['SS'] }}</div>
                </div>
                <div
                    class="border rounded p-2 text-center bg-green-600 text-white dark:bg-green-700 dark:border-green-800">
                    <div class="font-bold">S+</div>
                    <div>{{ achievementDistribution['S+'] }}</div>
                </div>
            </div>
        </div>

        <!-- 曲目类型分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md mb-4 p-3">
            <div class="mb-2">
                <h3 class="text-lg font-bold dark:text-gray-200">曲目类型分布</h3>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div
                    class="border rounded p-2 flex justify-between items-center bg-blue-500 text-white dark:bg-blue-600 dark:border-blue-700">
                    <div class="font-bold">标准</div>
                    <div>{{ songTypeDistribution['STANDARD'] }}</div>
                </div>
                <div
                    class="border rounded p-2 flex justify-between items-center bg-orange-500 text-white dark:bg-orange-600 dark:border-orange-700">
                    <div class="font-bold">DX</div>
                    <div>{{ songTypeDistribution['DX'] }}</div>
                </div>
            </div>
        </div>

        <!-- 难度系数分布 -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-md mb-4 p-3">
            <div class="mb-2">
                <h3 class="text-lg font-bold dark:text-gray-200">难度系数分布</h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div v-for="(count, level) in levelDistribution" :key="level"
                    class="border rounded p-2 flex justify-between items-center" :class="{
                        'bg-purple-900 text-white dark:bg-purple-950 dark:border-purple-900': String(level).includes('15'),
                        'bg-purple-700 text-white dark:bg-purple-800 dark:border-purple-700': String(level).includes('14'),
                        'bg-purple-500 text-white dark:bg-purple-600 dark:border-purple-500': String(level).includes('13'),
                        'bg-indigo-600 text-white dark:bg-indigo-700 dark:border-indigo-600': String(level).includes('12'),
                        'bg-blue-600 text-white dark:bg-blue-700 dark:border-blue-600': String(level).includes('11'),
                        'bg-teal-600 text-white dark:bg-teal-700 dark:border-teal-600': String(level).includes('10'),
                        'bg-green-700 text-white dark:bg-green-800 dark:border-green-700': String(level).includes('9'),
                        'bg-green-600 text-white dark:bg-green-700 dark:border-green-600': String(level).includes('8'),
                        'bg-green-500 text-white dark:bg-green-600 dark:border-green-500': parseInt(String(level)) < 8
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

<script setup lang="ts">
import { useServerStore } from '@/stores/server';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import type { CrawlerResult } from '@/types';
import { onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const serverStore = useServerStore();
const notificationStore = useNotificationStore();

const progress = ref(0);
const crawlerResults = ref<CrawlerResult[]>([]);
const statusText = ref('正在获取游戏数据...');
const phase = ref(1); // 1: 获取数据, 2: 上传数据, 3: 完成

onMounted(async () => {
    progress.value = 0;
    phase.value = 1;

    const dataInterval = setInterval(() => {
        if (progress.value >= 85 || phase.value >= 3) {
            clearInterval(dataInterval);
            if (phase.value < 2) {
                phase.value = 2;
                statusText.value = '正在上传数据至查分器...';
            }
        } else if (phase.value === 1 && progress.value < 40) {
            progress.value += 0.4;
        } else if (phase.value === 1 && progress.value < 60) {
            progress.value += 0.3;
        } else if (phase.value === 2 || progress.value < 85) {
            progress.value += 0.2;
        }
    }, 100);

    try {
        const params = route.fullPath.replace(route.path, '');
        statusText.value = '正在获取游戏数据';

        const resp = await userStore.axiosInstance.get("/accounts/update/callback" + params, { timeout: 120000 });
        if (resp.status !== 200) throw new Error("页面等待超时, 但您的分数可能已经上传成功");

        crawlerResults.value = resp.data;
        phase.value = 3;
        statusText.value = '数据同步完成';

        // 快速平滑过渡到100%
        const completionInterval = setInterval(() => {
            if (progress.value >= 100) {
                progress.value = 100;
                clearInterval(completionInterval);
            } else {
                progress.value += (100 - progress.value) / 5 + 2;
            }
        }, 50);
    } catch (error: any) {
        phase.value = 3;
        statusText.value = '同步过程中遇到错误';
        progress.value = 100;
        let message = error.response?.data?.detail || error.message;
        if (error.response?.status == 422) message = "请从微信页面中打开UsagiPass并重试";
        notificationStore.error("更新失败", message);
        router.push({ name: 'home' });
    }
});

const progressBarColor = computed(() => {
    if (phase.value === 1) return 'bg-blue-600';
    if (phase.value === 2) return 'bg-green-500';
    return 'bg-green-600';
});
</script>
<template>
    <h1 class="mt-2 text-2xl font-bold">更新查分器</h1>
    <h2 class="mt-1 mb-3 text-sm text-gray-700">将当前微信登录玩家的游戏数据同步至水鱼 / 落雪查分器</h2>
    <div
        class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full bg-white mb-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">更新状态</h1>
        </div>
        <div class="w-full flex flex-col items-center px-4 py-4">
            <p class="text-gray-600 mt-2 mb-2">{{ statusText }}</p>
            <div class="w-full bg-gray-200 rounded-full h-3 dark:bg-gray-700 relative mb-2">
                <div ref="progress-bar" :class="[progressBarColor, 'h-3 rounded-full progress-animation']"
                    :style="{ 'width': progress + '%' }"></div>
                <div class="absolute top-0 left-0 w-full h-full flex justify-center items-center">
                    <span class="text-xs font-medium" v-bind:class="{ 'text-white': progress >= 100 }">
                        {{ Math.floor(progress) }}%
                    </span>
                </div>
            </div>
            <div class="w-full flex justify-between text-xs text-gray-500 mt-1">
                <span class="w-1/3 text-left ml-2">获取数据</span>
                <span class="w-1/3 text-center">上传数据</span>
                <span class="w-1/3 text-right mr-2">完成</span>
            </div>
        </div>
    </div>
    <template v-for="result in crawlerResults">
        <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mb-2">
            <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                <h1 v-if="result.account_server == 3" class="font-bold text-white">成绩获取结果</h1>
                <h1 v-else class="font-bold text-white">{{ serverStore.serverNames[result.account_server] }}上传结果</h1>
            </div>
            <div class="flex items-center w-full mt-2">
                <div :class="result.success ? 'bg-green-500' : 'bg-red-500'" class="w-4 h-4 rounded-full ml-2 mr-1" />
                <div v-if="result.account_server == 3" class="flex flex-col p-2">
                    <span>
                        获取 {{ result.scores_num }} 个成绩 {{ result.success ? '成功' : '失败' }}
                    </span>
                    <span v-if="result.success" class="text-gray-600" style="font-size: 12px;">
                        用时: {{ result.elapsed_time.toFixed(2) }} 秒
                    </span>
                    <span v-if="!result.success" class="text-gray-600" style="font-size: 12px;">
                        失败原因: {{ result.err_msg }}
                    </span>
                </div>
                <div v-else class="flex flex-col p-2">
                    <span>
                        更新 {{ result.scores_num }} 个成绩 {{ result.success ? '成功' : '失败' }}
                    </span>
                    <span v-if="result.success" class="text-gray-600" style="font-size: 12px;">
                        用时: {{ result.elapsed_time.toFixed(2) }} 秒 <br>
                        Rating 变化: {{ result.from_rating }} -> {{ result.to_rating }}
                    </span>
                    <span v-if="!result.success" class="text-gray-600" style="font-size: 12px;">
                        失败原因: {{ result.err_msg }}
                    </span>
                </div>
            </div>
        </div>
    </template>
    <template v-if="progress >= 100">
        <div class="flex justify-end w-full mt-2 mr-2">
            <RouterLink class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                :to="{ name: 'home' }">
                回到首页
            </RouterLink>
        </div>
    </template>
</template>
<style scoped>
@keyframes pulse {
    50% {
        opacity: .8;
    }
}

.progress-animation {
    transition: width 0.3s ease-out;
    /* 加快过渡效果 */
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

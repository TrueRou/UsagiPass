<script setup lang="ts">
import { useServerStore } from '@/stores/server';
import { useUserStore } from '@/stores/user';
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const userStore = useUserStore();
const serverStore = useServerStore();
const route = useRoute();
const router = useRouter();
const crawlerResults = ref<CrawlerResult[][]>([]);

const progress = ref(0);
const progressBar = ref<HTMLDivElement | null>(null);

onMounted(async () => {
    progress.value = 0;

    const interval = setInterval(() => {
        if (progress.value >= 100) clearInterval(interval);
        else if (progress.value <= 80) progress.value++;
    }, 1200); // 60 seconds / 100 steps = 600ms per step

    try {
        const params = route.fullPath.replace(route.path, '');
        const resp = await userStore.axiosInstance.get("/accounts/update/callback" + params, { timeout: 120000 });
        if (resp.status !== 200) throw new Error("页面等待超时, 但您的分数可能已经上传成功");
        crawlerResults.value[0] = resp.data.filter((result: CrawlerResult) => result.account_server === 1);
        crawlerResults.value[1] = resp.data.filter((result: CrawlerResult) => result.account_server === 2);
        progress.value = 100;
    } catch (error: any) {
        progress.value = 100;
        let message = error.response.data.detail || error.message;
        if (error.response.status = 422) message = "请从微信页面中打开UsagiPass并重试";
        setTimeout(() => { alert(message); }, 200);
        router.push({ name: 'home' });
    }
});
</script>
<template>
    <h1 class="mt-2 text-2xl font-bold">更新查分器</h1>
    <h2 class="mt-1 mb-3 text-sm text-gray-700">将当前微信登录玩家的游戏数据同步至水鱼 / 落雪查分器</h2>
    <template v-if="progress < 100">
        <div
            class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full bg-white">
            <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                <h1 class="font-bold text-white">玩家分数上传</h1>
            </div>
            <div class="w-full flex flex-col items-center px-4 py-4">
                <p class="text-gray-600 mt-2">请稍候, 正在获取并上传分数数据<br>(大约需要60 ~ 120秒)...</p>
                <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                    <div ref="progressBar" class="bg-blue-600 h-2.5 rounded-full smooth pulse"
                        :style="{ 'width': progress + '%' }"></div>
                </div>
            </div>
        </div>
    </template>
    <template v-for="(results, index) in crawlerResults" v-if="progress >= 100">
        <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mb-2">
            <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                <h1 class="font-bold text-white">{{ serverStore.serverNames[index + 1] }}上传结果</h1>
            </div>
            <div class="flex items-center w-full mt-2" v-for="result in results">
                <div :class="result.success ? 'bg-green-500' : 'bg-red-500'" class="w-4 h-4 rounded-full ml-2 mr-1" />
                <div class="flex flex-col p-2">
                    <span>
                        更新 <b>{{ result.diff_label }}</b> 难度 {{ result.success ? '成功' : '失败' }}
                    </span>
                    <span class="text-gray-600" style="font-size: 12px;">
                        上传了 {{ result.scores_num }} 条数据
                    </span>
                </div>
            </div>
        </div>
    </template>
    <template v-if="progress >= 100">
        <div class="flex justify-end w-full mt-2 mr-2">
            <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                @click="router.push({ name: 'home' });">
                回到首页
            </button>
        </div>
    </template>
</template>
<style scoped>
@keyframes smooth {
    0% {
        width: 0%;
    }

    100% {
        width: 100%;
    }
}

@keyframes pulse {
    50% {
        opacity: .6;
    }
}

.smooth {
    animation: smooth 60s linear forwards;
}

.pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

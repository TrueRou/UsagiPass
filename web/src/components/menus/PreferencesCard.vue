<script setup lang="tsx">
import { ref } from 'vue';
import { formatDate } from '@/utils';
import { useCardStore } from '@/stores/card';
import Prompt from '@/components/widgets/Prompt.vue';
import TermsLink from '@/components/widgets/TermsLink.vue';



const cardStore = useCardStore();

if (!cardStore.cardPreference) await cardStore.refreshCard();
const isActivated = ref(Boolean(cardStore.cardAccount));
const activationCode = ref('');
const showActivationPrompt = ref(false);

const openActivationPrompt = () => {
    showActivationPrompt.value = true;
};

const confirmActivation = async () => {
    await activateCard();
    showActivationPrompt.value = false;
};

const cancelActivation = () => {
    activationCode.value = '';
    showActivationPrompt.value = false;
};

const activateCard = async () => {
    if (!activationCode.value) return;

    try {
        await cardStore.createAccount(activationCode.value);
        await cardStore.refreshCard();
        isActivated.value = Boolean(cardStore.cardAccount);
    } finally {
        activationCode.value = '';
    }
};
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">卡片激活</h1>
        </div>

        <!-- 卡片激活状态 -->
        <div class="flex justify-between items-center w-full mt-3 px-4">
            <span class="font-medium">激活状态:</span>
            <span class="font-bold" :class="isActivated ? 'text-green-600' : 'text-red-600'">
                {{ isActivated ? '已激活' : '未激活' }}
            </span>
        </div>

        <!-- 卡片激活按钮 -->
        <div v-if="!isActivated" class="flex justify-center w-full mt-3 px-4">
            <button @click="openActivationPrompt"
                class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 w-full">
                激活卡片
            </button>
        </div>

        <!-- 已激活卡片的详细信息 -->
        <div v-if="isActivated && cardStore.cardAccount" class="w-full mt-3 mb-3 px-4">
            <div class="bg-gray-100 rounded p-3 border border-gray-300">
                <h2 class="font-bold text-lg mb-2 text-blue-600">卡片信息</h2>

                <div class="grid grid-cols-2 gap-2">
                    <div class="flex flex-col">
                        <span class="text-gray-600 text-sm">激活时间</span>
                        <span class="font-medium">{{ formatDate(cardStore.cardAccount.created_at) }}</span>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-gray-600 text-sm">最后活动</span>
                        <span class="font-medium">
                            {{ new Date(cardStore.cardAccount.last_activity_at).toLocaleString() }}
                        </span>
                    </div>
                </div>

                <div v-if="cardStore.cardAccount.player_bests" class="mt-3">
                    <h2 class="font-bold text-lg mb-2 text-blue-600">成绩信息</h2>
                    <div class="grid grid-cols-2 gap-2 mt-1">
                        <div class="flex flex-col">
                            <span class="text-gray-600 text-sm">总 Rating</span>
                            <span class="font-medium">{{ cardStore.cardAccount.player_bests.all_rating }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-gray-600 text-sm">最后更新</span>
                            <span class="font-medium">{{ new
                                Date(cardStore.cardAccount.last_updated_at).toLocaleString() }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 激活对话框 -->
        <Prompt v-model="activationCode" :show="showActivationPrompt" text="请输入卡片激活码" placeholder="扫描二维码或输入激活码"
            @confirm="confirmActivation" @cancel="cancelActivation">
            <TermsLink />
        </Prompt>
    </div>

    <div class="flex justify-end w-full mt-2 mr-5">
        <RouterLink to="/" @click.prevent="$router.go(-1)"
            class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 inline-block">
            返回
        </RouterLink>
    </div>
</template>
<style scoped>
input {
    outline-style: none;
    border: 2px solid #000;
    border-radius: 5px;
    width: 200px;

    @media (max-width: 600px) {
        width: 160px;
    }

    @media (max-width: 380px) {
        width: 140px;
    }

    height: 44.5px;
    padding: 0;
    padding: 10px 10px;
    box-sizing: border-box;

    &:focus {
        border-color: #60a5fa;
        outline: 0;
        -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
        box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
    }
}

select {
    background: #fafdfe;
    width: 200px;

    @media (max-width: 600px) {
        width: 160px;
    }

    @media (max-width: 380px) {
        width: 140px;
    }

    height: 44.5px;
    padding: 10px 10px;
    box-sizing: border-box;
    border: 2px solid #000;
    border-radius: 5px;
}
</style>
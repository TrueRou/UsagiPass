<script setup lang="tsx">
import { useCardStore } from '@/stores/card';
import { ref } from 'vue';
import Prompt from '@/components/widgets/Prompt.vue';

const cardStore = useCardStore();

if (!cardStore.cardProfile) await cardStore.refreshCard();
const isActivated = ref(Boolean(cardStore.cardProfile && cardStore.cardProfile.user_id));
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
        isActivated.value = Boolean(cardStore.cardProfile && cardStore.cardProfile.user_id);
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

        <!-- 卡片ID信息 -->
        <div class="flex justify-between items-center w-full mt-3 px-4">
            <span class="font-medium">卡片 ID:</span>
            <span class="font-bold">{{ cardStore.cardProfile?.card_id }}</span>
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

        <!-- 激活对话框 -->
        <Prompt v-model="activationCode" :show="showActivationPrompt" text="请输入卡片激活码" placeholder="扫描二维码或输入激活码"
            @confirm="confirmActivation" @cancel="cancelActivation" />
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
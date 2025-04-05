<script setup lang="tsx">
import { ref } from 'vue';
import { formatDate } from '@/utils/formatUtils';
import { useCardStore } from '@/stores/card';
import Prompt from '@/components/widgets/Prompt.vue';
import TermsLink from '@/components/widgets/TermsLink.vue';
import { CardStatus } from '@/types';
import { useNotificationStore } from '@/stores/notification';
import { checkNfcEnvironment } from '@/utils/nfcUtils';

const cardStore = useCardStore();
const notificationStore = useNotificationStore();

if (!cardStore.cardProfile) await cardStore.refreshCard();
const isActivated = ref(Boolean(cardStore.cardProfile?.status === CardStatus.ACTIVATED));
const activationCode = ref('');
const showActivationPrompt = ref(false);
const tapCount = ref(0);
const showNfcSettings = ref(false);

const handleActivationDateTap = () => {
    tapCount.value++;
    if (tapCount.value >= 5) { // 5次点击触发
        if (checkNfcEnvironment()) {
            showNfcSettings.value = true;
        } else {
            notificationStore.warning('不支持Web NFC的环境', '请在手机端使用Chrome浏览器访问');
            tapCount.value = 0; // 重置点击次数
        }
    }
};

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

    await cardStore.createAccount(activationCode.value);
    await cardStore.refreshCard();
    activationCode.value = '';
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
            <span class="font-bold no-select"
                :class="cardStore.cardProfile?.accounts ? 'text-green-600' : 'text-gray-600'"
                @click="handleActivationDateTap">
                {{ cardStore.cardProfile?.accounts ? '已激活' : '未激活' }}
            </span>
        </div>

        <!-- 卡片未激活 显示激活按钮 -->
        <div v-if="!cardStore.cardProfile?.accounts" class="flex justify-center w-full mt-3 px-4">
            <button @click="openActivationPrompt"
                class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 w-full">
                激活卡片
            </button>
        </div>

        <!-- 卡片已激活 显示激活信息 -->
        <template v-if="isActivated && cardStore.cardProfile?.accounts">
            <div class="flex justify-between items-center w-full mt-3 px-4">
                <span class="font-medium">激活时间:</span>
                <span class="font-bold">
                    {{ formatDate(cardStore.cardProfile.accounts.created_at) }}
                </span>
            </div>
            <div class="flex justify-between items-center w-full mt-3 px-4">
                <span class="font-medium">总 Rating:</span>
                <span class="font-bold">
                    {{ cardStore.cardProfile.accounts.player_bests.all_rating }}
                </span>
            </div>
        </template>

        <!-- 激活对话框 -->
        <Prompt v-model="activationCode" :show="showActivationPrompt" text="请输入卡片激活码" placeholder="输入二维码扫描内容"
            @confirm="confirmActivation" @cancel="cancelActivation">
            <TermsLink />
        </Prompt>
    </div>

    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">NFC模式</h1>
        </div>

        <div class="w-full mt-3 mb-3 px-4">
            <div class="mb-4">
                <p class="text-gray-800 font-medium text-sm mb-2">
                    您可以修改卡片的NFC模式以适应不同的设备环境。
                </p>
                <p class="text-gray-600 text-xs leading-relaxed">
                    <span class="font-semibold">兼容模式:</span> 所有支持NFC的设备均可使用, 但可能每次都要点击确认<br>
                    <span class="font-semibold">快速模式:</span> 无需二次确认即可跳转, 但缺失浏览器可能会跳转应用商店
                </p>
            </div>
            <div class="flex justify-center">
                <RouterLink to="/nfc"
                    class="bg-indigo-600 text-white font-bold py-2.5 px-4 rounded-md hover:bg-indigo-700 active:bg-indigo-800 transition-colors duration-200 ease-in-out shadow-sm inline-block w-full text-center">
                    修改卡片模式
                </RouterLink>
            </div>
        </div>
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

.no-select {
    user-select: none;
}
</style>
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useCardStore } from '@/stores/card';
import DXBaseView from './DXBaseView.vue';
import type { PreferencePublic } from '@/types';
import CardBests from '@/components/CardBests.vue';

const cardStore = useCardStore();
const activeView = ref(0); // 0: DXBaseView, 1: ScoreListView
const touchStartX = ref(0);
const touchEndX = ref(0);
const minSwipeDistance = 50;

if (!cardStore.cardProfile) await cardStore.refreshCard();
const cardPreference = ref<PreferencePublic>(JSON.parse(JSON.stringify(cardStore.cardProfile!.preferences)));
const showActivationDialog = ref(cardStore.cardProfile!.user_id && cardStore.cardProfile!.preferences.skip_activation);
const activationCode = ref('');

const activateCard = async () => {
    if (activationCode.value) {
        await cardStore.activateCard(activationCode.value);
        await cardStore.refreshCard()
        showActivationDialog.value = false;
    }
};

const skipActivation = async () => {
    if (cardStore.cardProfile) {
        cardStore.cardProfile.preferences.skip_activation = true;
        await cardStore.patchPreferences();
        showActivationDialog.value = false;
    }
};

const applyPreferences = () => {
    if (cardStore.cardProfile!.player_rating != -1) {
        cardPreference.value.dx_rating ||= String(cardStore.cardProfile!.player_rating);
    }
}

applyPreferences();

const handleTouchStart = (e: TouchEvent) => {
    touchStartX.value = e.changedTouches[0].screenX;
};

const handleTouchEnd = (e: TouchEvent) => {
    touchEndX.value = e.changedTouches[0].screenX;
    handleSwipe();
};

const handleSwipe = () => {
    const distance = touchEndX.value - touchStartX.value;
    if (Math.abs(distance) < minSwipeDistance) return;

    if (distance > 0) {
        if (activeView.value > 0) activeView.value--;
    } else {
        if (activeView.value < 1) activeView.value++;
    }
};

const switchToView = (index: number) => {
    activeView.value = index;
};

onMounted(async () => {
    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);
});

onUnmounted(() => {
    document.removeEventListener('touchstart', handleTouchStart);
    document.removeEventListener('touchend', handleTouchEnd);
});
</script>

<template>
    <div class="w-full h-full overflow-hidden relative">
        <!-- 视图容器 -->
        <div class="flex w-[200%] h-full transition-transform duration-300 ease-in-out"
            :style="{ transform: `translateX(-${activeView * 50}%)` }">
            <div class="flex-none w-1/2 h-full overflow-y-auto relative">
                <DXBaseView :preferences="cardPreference" timeLimit="12:00:00"
                    class="h-full w-full absolute top-0 left-0" :settingsRoute="{ name: 'preferencesCard' }" />
            </div>
            <div class="flex-none w-1/2 h-full overflow-y-auto relative">
                <CardBests :key="cardStore.cardProfile!.user_id" class="h-full w-full absolute top-0 left-0" />
            </div>
        </div>

        <!-- 指示器和导航 -->
        <div class="fixed bottom-10 left-1/2 transform -translate-x-1/2 flex gap-2.5 z-10">
            <div class="w-2.5 h-2.5 rounded-full cursor-pointer"
                :class="{ 'bg-white': activeView === 0, 'bg-white/50': activeView !== 0 }" @click="switchToView(0)">
            </div>
            <div class="w-2.5 h-2.5 rounded-full cursor-pointer"
                :class="{ 'bg-white': activeView === 1, 'bg-white/50': activeView !== 1 }" @click="switchToView(1)">
            </div>
        </div>

        <!-- 激活对话框 -->
        <div v-if="showActivationDialog" class="fixed inset-0 bg-black/70 flex justify-center items-center z-10">
            <div class="bg-white p-5 rounded-lg w-[90%] max-w-md shadow-md text-gray-800">
                <p>您的卡片尚未激活，绑定微信来进行激活。</p>

                <div class="my-5">
                    <input id="activation-code" v-model="activationCode" type="text"
                        class="w-full p-2.5 border border-gray-300 rounded text-base" placeholder="请输入二维码扫描后的内容" />
                </div>

                <div class="flex justify-between mt-5">
                    <button @click="skipActivation"
                        class="px-5 py-2.5 rounded font-bold bg-gray-100 text-gray-800">跳过</button>
                    <button @click="activateCard"
                        class="px-5 py-2.5 rounded font-bold bg-green-600 text-white">激活</button>
                </div>

                <p class="text-xs text-gray-500 mt-4">* 跳过激活后，查分功能将无法使用</p>
                <p class="text-xs text-gray-500">* 您可以随时进行激活，一旦激活后不可换绑</p>
            </div>
        </div>
    </div>
</template>

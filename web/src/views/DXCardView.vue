<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useCardStore } from '@/stores/card';
import DXBaseView from './DXBaseView.vue';
import type { CardProfile, PreferencePublic } from '@/types';
import ScoreListView from './ScoreListView.vue';
import CardBests from '@/components/CardBests.vue';

const cardStore = useCardStore();
const cardProfile = ref<CardProfile>(await cardStore.fetchCard(history.state.uuid));
const cardPreference = ref<PreferencePublic>(JSON.parse(JSON.stringify(cardProfile.value!.preferences)));

const applyPreferences = () => {
    if (cardProfile.value.player_rating != -1) cardPreference.value.dx_rating ||= String(cardProfile.value.player_rating);
}

applyPreferences();

// 滑动相关状态和变量
const activeView = ref(0); // 0: DXBaseView, 1: ScoreListView
const touchStartX = ref(0);
const touchEndX = ref(0);
const minSwipeDistance = 50; // 最小滑动距离

// 处理触摸开始事件
const handleTouchStart = (e: TouchEvent) => {
    touchStartX.value = e.changedTouches[0].screenX;
};

// 处理触摸结束事件
const handleTouchEnd = (e: TouchEvent) => {
    touchEndX.value = e.changedTouches[0].screenX;
    handleSwipe();
};

// 处理滑动方向判断和视图切换
const handleSwipe = () => {
    const distance = touchEndX.value - touchStartX.value;

    if (Math.abs(distance) < minSwipeDistance) return;

    if (distance > 0) {
        // 右滑，显示前一个页面
        if (activeView.value > 0) activeView.value--;
    } else {
        // 左滑，显示后一个页面
        if (activeView.value < 1) activeView.value++;
    }
};

// 直接切换到指定页面
const switchToView = (index: number) => {
    activeView.value = index;
};

// 挂载和卸载事件监听器
onMounted(() => {
    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);
});

onUnmounted(() => {
    document.removeEventListener('touchstart', handleTouchStart);
    document.removeEventListener('touchend', handleTouchEnd);
});
</script>

<template>
    <div class="swipe-container">
        <!-- 视图容器 -->
        <div class="views-container" :style="{ transform: `translateX(-${activeView * 50}%)` }">
            <div class="view-item">
                <DXBaseView :preferences="cardPreference" timeLimit="12:00:00" settingsRoute="preferences" />
            </div>
            <div class="view-item">
                <CardBests />
            </div>
        </div>

        <!-- 指示器和导航 -->
        <div class="view-indicator">
            <div class="indicator-dot" :class="{ active: activeView === 0 }" @click="switchToView(0)"></div>
            <div class="indicator-dot" :class="{ active: activeView === 1 }" @click="switchToView(1)"></div>
        </div>
    </div>
</template>

<style scoped>
.swipe-container {
    width: 100%;
    height: 100%;
    overflow: hidden;
    position: relative;
}

.views-container {
    display: flex;
    width: 200%;
    height: 100%;
    transition: transform 0.3s ease;
}

.view-item {
    flex: 0 0 50%;
    width: 50%;
    height: 100%;
    overflow-y: auto;
    position: relative;
}

.view-item>* {
    height: 100%;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
}

.view-indicator {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    z-index: 10;
}

.indicator-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
}

.indicator-dot.active {
    background-color: white;
}
</style>
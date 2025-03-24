<script setup lang="ts">
import { useDraftStore } from '@/stores/draft';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import type { Card, Preference } from '@/types';
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';
import DXBaseView from '@/views/DXBaseView.vue';
import { getShortUuid, formatDate, getOrderStatus } from '@/utils';
import Prompt from '@/components/widgets/Prompt.vue';

const draftStore = useDraftStore();
const userStore = useUserStore();
const notificationStore = useNotificationStore();

const cards = ref<Card[]>([]);
const phoneNumber = ref("");
const selectedCard = ref<Card | null>(null);
const previewPreferences = ref<Preference | null>(null);
const showPreview = ref(false);
const showStatusConfirm = ref(false);
const dateFilter = ref<'all' | '3days' | 'week' | 'month'>('all');
const typeFilter = ref<'all' | 'draft'>('all');
const showDeleteConfirm = ref(false);
const draftToDelete = ref("");
const selectedCards = ref<Set<string>>(new Set());
const isDownloading = ref(false);

const fetchCards = async () => {
    try {
        cards.value = (await userStore.axiosInstance.get('/cards')).data
    } catch (error: any) {
        notificationStore.error("获取卡片失败", error.response.data.detail || "未知错误");
        throw error
    }
};

const updateCardStatus = async (uuid: string, mode: 'CONFIRMED' | 'UNSET') => {
    // 再次检查卡片是否已激活（防止对话框打开后卡片状态发生变化）
    const card = cards.value.find(c => c.uuid === uuid);
    if (card && card.user_id) {
        notificationStore.warning(
            "无法修改状态",
            "已激活的卡片不允许修改状态。"
        );
        showStatusConfirm.value = false;
        return;
    }

    try {
        await userStore.axiosInstance.patch(`/cards/${uuid}?mode=${mode}`);
        notificationStore.success("状态更新成功", `卡片状态已更新为${mode === 'CONFIRMED' ? '已确认' : '草稿'}`);
        await fetchCards();
        showStatusConfirm.value = false;
    } catch (error: any) {
        notificationStore.error("状态更新失败", error.response.data.detail || "未知错误");
        throw error
    }
};

const deleteDraft = async (uuid: string) => {
    await draftStore.deleteDraft(uuid)
    notificationStore.success("删除成功", "草稿已删除");
    await fetchCards();
};

const confirmDelete = (uuid: string) => {
    draftToDelete.value = uuid;
    showDeleteConfirm.value = true;
};

const handleConfirmDelete = () => {
    if (draftToDelete.value) {
        deleteDraft(draftToDelete.value);
        showDeleteConfirm.value = false;
        draftToDelete.value = "";
    }
};

const handleCancelDelete = () => {
    showDeleteConfirm.value = false;
    draftToDelete.value = "";
};

const filteredCards = computed(() => {
    let result = [...cards.value];

    // 按手机号码筛选
    if (phoneNumber.value) {
        result = result.filter(card => {
            const phoneNum = card.phone_number || '未知号码';
            return phoneNum.includes(phoneNumber.value);
        });
    }

    // 按是否为草稿筛选
    if (typeFilter.value === 'draft') {
        result = result.filter(card => !card.card_id);
    }

    // 按时间段筛选
    if (dateFilter.value !== 'all') {
        const now = new Date();
        let startDate: Date;

        switch (dateFilter.value) {
            case '3days':
                startDate = new Date(now);
                startDate.setDate(now.getDate() - 3);
                break;
            case 'week':
                startDate = new Date(now);
                startDate.setDate(now.getDate() - 7);
                break;
            case 'month':
                startDate = new Date(now);
                startDate.setMonth(now.getMonth() - 1);
                break;
            default:
                startDate = new Date(0);
        }

        result = result.filter(card => new Date(card.created_at) >= startDate);
    }

    // 默认排序（最新的在前面）
    result.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
    });

    return result;
});

// 将卡片按手机号码分组
const groupedCards = computed(() => {
    const groups: Record<string, Card[]> = {};

    filteredCards.value.forEach(card => {
        const phoneNumber = card.phone_number || '未知号码';
        if (!groups[phoneNumber]) {
            groups[phoneNumber] = [];
        }
        groups[phoneNumber].push(card);
    });

    return Object.entries(groups).map(([phoneNumber, cards]) => ({
        phoneNumber,
        cards
    }));
});

const previewCard = async (card: Card) => {
    selectedCard.value = card;
    previewPreferences.value = await draftStore.fetchPreferences(card.uuid);
    showPreview.value = true;
};

const closePreview = () => {
    showPreview.value = false;
    selectedCard.value = null;
};

const showStatusDialog = (card: Card) => {
    // 检查卡片是否已激活
    if (card.user_id) {
        notificationStore.warning(
            "无法修改状态",
            "已激活的卡片不允许修改状态。该卡片已有用户使用。"
        );
        return;
    }
    selectedCard.value = card;
    showStatusConfirm.value = true;
};

const toggleCardSelection = (uuid: string) => {
    if (selectedCards.value.has(uuid)) {
        selectedCards.value.delete(uuid);
    } else {
        selectedCards.value.add(uuid);
    }
};

const toggleGroupSelection = (groupCards: Card[]) => {
    const allSelected = groupCards.every(card => selectedCards.value.has(card.uuid));

    if (allSelected) {
        groupCards.forEach(card => {
            selectedCards.value.delete(card.uuid);
        });
    } else {
        groupCards.forEach(card => {
            selectedCards.value.add(card.uuid);
        });
    }
};

const isGroupAllSelected = (groupCards: Card[]) => {
    return groupCards.length > 0 && groupCards.every(card => selectedCards.value.has(card.uuid));
};

const isGroupPartialSelected = (groupCards: Card[]) => {
    const selectedCount = groupCards.filter(card => selectedCards.value.has(card.uuid)).length;
    return selectedCount > 0 && selectedCount < groupCards.length;
};

const downloadBatchScreenshots = async () => {
    if (selectedCards.value.size === 0) {
        notificationStore.warning("请先选择卡片", "您需要至少选择一张卡片");
        return;
    }

    try {
        isDownloading.value = true;

        // 过滤出已确认的卡片（有card_id的卡片）
        const selectedCardsList = cards.value.filter(card => selectedCards.value.has(card.uuid));
        const confirmedCards = selectedCardsList.filter(card => card.card_id);
        const draftCards = selectedCardsList.filter(card => !card.card_id);

        // 如果有草稿卡片，显示警告
        if (draftCards.length > 0) {
            notificationStore.warning(
                "草稿卡片已被过滤",
                `${draftCards.length}张草稿卡片不会被下载，因为它们尚未确认。只有已确认的卡片将被下载。`
            );

            // 如果过滤后没有可下载的卡片，直接返回
            if (confirmedCards.length === 0) {
                notificationStore.warning("无法下载", "您选择的卡片中没有已确认的卡片，请先确认卡片。");
                isDownloading.value = false;
                return;
            }
        }

        const uuidsToDownload = confirmedCards.map(card => card.uuid);

        const a = document.createElement('a');
        a.style.display = 'none';
        document.body.appendChild(a);

        const response = await userStore.axiosInstance.post('/cards/batch/screenshot',
            uuidsToDownload,
            { responseType: 'blob', timeout: 60000 }
        );

        const url = window.URL.createObjectURL(new Blob([response.data]));
        a.href = url;
        a.download = `cards_${new Date().toISOString().slice(0, 10)}.zip`;
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        notificationStore.success("下载成功", `已成功下载${confirmedCards.length}张卡片的截图`);
    } catch (error: any) {
        notificationStore.error("下载失败", error.response?.data?.detail || "未知错误");
    } finally {
        isDownloading.value = false;
    }
};

const clearSelection = () => {
    selectedCards.value.clear();
};

const preferencesReadOnly = computed(() => {
    if (!previewPreferences.value) return null;
    return JSON.parse(JSON.stringify(previewPreferences.value));
});

fetchCards();
</script>

<template>
    <!-- 添加删除确认对话框 -->
    <Prompt :show="showDeleteConfirm" text="确定要删除这个草稿吗？此操作无法撤销。" @confirm="handleConfirmDelete"
        @cancel="handleCancelDelete" />

    <!-- 预览弹窗 -->
    <div v-if="showPreview && previewPreferences"
        class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg w-full overflow-hidden" style="max-width: 30rem;">
            <div class="p-4 bg-blue-400 text-white flex justify-between items-center">
                <span class="font-bold text-nowrap">卡面预览 - 订单号: {{ getShortUuid(selectedCard!.uuid) }}</span>
                <button @click="closePreview" class="text-white hover:text-gray-200">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="p-4 flex flex-col items-center">
                <div class="flex flex-1 preview-radius w-full" style="max-width: 100vw;">
                    <DXBaseView :preferences="preferencesReadOnly" />
                </div>
            </div>
        </div>
    </div>

    <!-- 状态更新确认弹窗 -->
    <div v-if="showStatusConfirm && selectedCard"
        class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg w-full overflow-hidden" style="max-width: 30rem;">
            <div class="p-4 bg-blue-400 text-white">
                <span class="font-bold">更新订单状态 - {{ getShortUuid(selectedCard.uuid) }}</span>
            </div>
            <div class="p-6">
                <p v-if="selectedCard.user_id" class="text-red-600 font-medium mb-4">
                    警告：该卡片已被激活，不应修改状态。
                </p>
                <p class="mb-4">当前状态:
                    <span :class="{
                        'bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full font-bold': !selectedCard.card_id,
                        'bg-green-100 text-green-800 px-2 py-1 rounded-full font-bold': selectedCard.card_id && !selectedCard.user_id,
                        'bg-blue-100 text-blue-800 px-2 py-1 rounded-full font-bold': selectedCard.user_id
                    }">
                        {{ getOrderStatus(selectedCard) }}
                    </span>
                </p>
                <p class="mb-6">请选择要更新的状态:</p>
                <div class="flex justify-end gap-3">
                    <button @click="showStatusConfirm = false"
                        class="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600">
                        取消
                    </button>
                    <button @click="updateCardStatus(selectedCard.uuid, 'UNSET')"
                        class="bg-yellow-500 text-white py-2 px-4 rounded hover:bg-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed">
                        设为草稿
                    </button>
                    <button @click="updateCardStatus(selectedCard.uuid, 'CONFIRMED')"
                        class="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed">
                        设为已确认
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="w-full p-4">
        <!-- 搜索和筛选区域 -->
        <div class="flex flex-col bg-white p-4 pt-0">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div class="flex flex-1 items-center">
                    <input v-model="phoneNumber" type="text" placeholder="按手机号过滤..."
                        class="flex-1 p-2 border border-gray-300 rounded mr-2 w-full md:w-auto">
                </div>

                <div class="flex items-center gap-4 flex-wrap">
                    <!-- 改为按钮选择样式 -->
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="text-gray-700">类型:</span>
                        <div class="flex border border-gray-300 rounded-md overflow-hidden">
                            <button @click="typeFilter = 'all'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': typeFilter === 'all', 'bg-gray-100 hover:bg-gray-200': typeFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium">
                                全部
                            </button>
                            <button @click="typeFilter = 'draft'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': typeFilter === 'draft', 'bg-gray-100 hover:bg-gray-200': typeFilter !== 'draft' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                仅草稿
                            </button>
                        </div>
                    </div>

                    <div class="flex flex-wrap items-center gap-2">
                        <span class="text-gray-700">时间:</span>
                        <div class="flex border border-gray-300 rounded-md overflow-hidden">
                            <button @click="dateFilter = 'all'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'all', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium">
                                全部
                            </button>
                            <button @click="dateFilter = '3days'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': dateFilter === '3days', 'bg-gray-100 hover:bg-gray-200': dateFilter !== '3days' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                三日内
                            </button>
                            <button @click="dateFilter = 'week'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'week', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'week' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                一周内
                            </button>
                            <button @click="dateFilter = 'month'; fetchCards()"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'month', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'month' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                一月内
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center h-8">
                <div class="flex items-center">
                    <span class="text-gray-600 mr-4" v-if="selectedCards.size == 0">总计: {{ filteredCards.length }}
                        条记录</span>
                    <!-- 添加选中计数 -->
                    <span v-if="selectedCards.size > 0" class="text-blue-600 font-medium">
                        已选择: {{ selectedCards.size }} 张卡片
                    </span>
                </div>
                <div class="flex items-center gap-2">
                    <!-- 批量下载按钮 -->
                    <button v-if="selectedCards.size > 0" @click="downloadBatchScreenshots" :disabled="isDownloading"
                        class="text-white bg-blue-600 hover:bg-blue-700 py-1.5 px-3 rounded text-sm font-medium flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
                        <svg v-if="isDownloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                            viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        下载卡面
                    </button>
                    <!-- 清除选择按钮 -->
                    <button v-if="selectedCards.size > 0" @click="clearSelection"
                        class="text-gray-600 hover:text-gray-800 py-1.5 px-2 rounded text-sm flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                    <!-- 刷新按钮 -->
                    <button @click="fetchCards" class="text-blue-600 hover:text-blue-800">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- 卡片列表 -->
        <div v-if="groupedCards.length === 0" class="text-center py-10">
            <p class="text-gray-600">没有找到符合条件的卡片</p>
        </div>

        <div v-else>
            <div v-for="(group, index) in groupedCards" :key="group.phoneNumber" class="mb-8 group-container">
                <!-- 手机号码分组标题 -->
                <div class="group-header flex justify-between items-center">
                    <span>手机号码: {{ group.phoneNumber }} ({{ group.cards.length }}张卡片)</span>

                    <!-- 全选/取消全选分组按钮 -->
                    <div class="flex items-center">
                        <button @click="toggleGroupSelection(group.cards)"
                            class="text-white hover:text-gray-200 flex items-center text-sm">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                fill="currentColor">
                                <rect v-if="isGroupAllSelected(group.cards)" width="16" height="16" x="2" y="2"
                                    rx="2" />
                                <path v-else-if="isGroupPartialSelected(group.cards)" fill-rule="evenodd"
                                    d="M3 5a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm0 0h14v10a2 2 0 01-2 2H5a2 2 0 01-2-2V5z"
                                    clip-rule="evenodd" />
                                <path v-else fill-rule="evenodd"
                                    d="M5 3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 2h10v10H5V5z"
                                    clip-rule="evenodd" />
                            </svg>
                            {{ isGroupAllSelected(group.cards) ? '取消全选' : '全选分组' }}
                        </button>
                    </div>
                </div>

                <div v-for="card in group.cards" :key="card.uuid"
                    class="bg-white shadow mb-1 overflow-hidden group-card"
                    :class="{ 'border-2 border-blue-500': selectedCards.has(card.uuid) }">
                    <div class="border-b border-gray-200 bg-gray-50 px-4 py-3 flex justify-between items-center">
                        <div class="flex items-center">
                            <!-- 添加勾选框 -->
                            <div class="mr-2 flex items-center">
                                <input type="checkbox" :checked="selectedCards.has(card.uuid)"
                                    @change="toggleCardSelection(card.uuid)" class="h-4 w-4 cursor-pointer">
                            </div>
                            <div>
                                <span class="font-bold">订单号: {{ getShortUuid(card.uuid) }}</span>
                                <span :class="{
                                    'ml-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-bold': !card.card_id && !card.user_id,
                                    'ml-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-bold': card.card_id && !card.user_id,
                                    'ml-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-bold': card.user_id && card.card_id
                                }">
                                    {{ getOrderStatus(card) }}
                                </span>
                            </div>
                        </div>
                        <span class="text-sm text-gray-600">{{ formatDate(card.created_at) }}</span>
                    </div>

                    <div class="p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <span class="text-gray-700">
                                    <span class="font-medium">卡片ID:</span> {{ card.card_id || '未分配' }}
                                </span>
                            </div>
                        </div>

                        <div class="flex flex-wrap gap-2">
                            <!-- 预览按钮 -->
                            <button @click="previewCard(card)"
                                class="bg-purple-500 text-white py-2 px-4 rounded hover:bg-purple-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path d="M10 12a2 2 0 100-4 2 2 0 000-4z" />
                                    <path fill-rule="evenodd"
                                        d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                                        clip-rule="evenodd" />
                                </svg>
                                预览
                            </button>

                            <!-- 编辑按钮 -->
                            <RouterLink :to="{ name: 'designer', params: { uuid: card.uuid } }"
                                class="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path
                                        d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                </svg>
                                编辑
                            </RouterLink>

                            <!-- 状态按钮 -->
                            <button @click="showStatusDialog(card)" :class="{
                                'bg-amber-500 hover:bg-amber-600': !card.user_id,
                                'bg-gray-400 hover:bg-gray-500': card.user_id
                            }" class="text-white py-2 px-4 rounded flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z"
                                        clip-rule="evenodd" />
                                </svg>
                                更新
                            </button>

                            <!-- 删除按钮 - 修改点击事件 -->
                            <button v-if="!card.card_id" @click="confirmDelete(card.uuid)"
                                class="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path fill-rule="evenodd"
                                        d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                        clip-rule="evenodd" />
                                </svg>
                                删除
                            </button>
                            <!-- 写卡按钮 -->
                            <button v-if="card.card_id"
                                class="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 30 30"
                                    fill="currentColor" stroke="currentColor" stroke-width="0.6">
                                    <path
                                        d="m 20 4.79296 v 18.10352 l -9 -9 v 3 c 0 0 8 9 9 9 h 0.210938 C 20.845635 25.55074 21.44166 25.14619 22 24.69531 v -18.59766 c -0.618707 -0.49963 -1.288408 -0.93504 -2 -1.30469 z M 8.7890625 4.89648 C 8.1543654 5.24222 7.5583404 5.64677 7 6.09765 v 18.59766 c 0.6187068 0.49963 1.2884078 0.93504 2 1.30469 v -18.10352 l 9 9 v -3 c 0 0 -8 -9 -9 -9 z" />
                                </svg>
                                写卡
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.preview-radius {
    border-radius: 16px;
    mask-image: radial-gradient(circle, white 100%, black 100%);
    -webkit-mask-image: -webkit-radial-gradient(circle, white 100%, black 100%);
    overflow: hidden;
}

input[type="checkbox"] {
    border-radius: 0.25rem;
    border-color: #d1d5db;
    color: #2563eb;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

input[type="checkbox"]:focus {
    border-color: #93c5fd;
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

/* 改进的分组视觉效果 - 使用黑白明暗对比 */
.group-container {
    position: relative;
    border-radius: 0.5rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
    background: linear-gradient(to right, #2d3748, #4a5568);
    margin-bottom: 1.5rem;
    padding-bottom: 0.25rem;
}

.group-header {
    background: linear-gradient(to right, #2d3748, #4a5568);
    color: white;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem 0.5rem 0 0;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.025em;
}

.group-card {
    border-radius: 0.5rem;
    margin: 0 0.5rem 0.5rem 0.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    background-color: white;
}

/* 单独一张卡片时的样式 */
.group-container:has(.group-card:only-child) .group-card {
    border-radius: 0.25rem;
}

input[type="date"] {
    min-width: 150px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* 添加选中状态的样式 */
input[type="checkbox"] {
    accent-color: #2563eb;
}
</style>

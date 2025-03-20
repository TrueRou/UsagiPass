<script setup lang="ts">
import { useDraftStore } from '@/stores/draft';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import type { Card, PreferencePublic } from '@/types';
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';
import DXBaseView from '@/views/DXBaseView.vue';

const draftStore = useDraftStore();
const userStore = useUserStore();
const notificationStore = useNotificationStore();

const cards = ref<Card[]>([]);
const loading = ref(false);
const phoneNumber = ref("");
const selectedCard = ref<Card | null>(null);
const previewPreferences = ref<PreferencePublic | null>(null);
const showPreview = ref(false);
const showStatusConfirm = ref(false);
const sortByNewest = ref(true);
const showOnlyDrafts = ref(false);

// 获取所有卡片或按电话号码筛选
const fetchCards = async () => {
    loading.value = true;
    try {
        if (phoneNumber.value) {
            cards.value = await draftStore.fetchDrafts(phoneNumber.value);
        } else {
            // 获取所有卡片
            const response = await userStore.axiosInstance.get('/cards');
            cards.value = response.data;
        }
    } catch (error) {
        console.error("Error fetching cards:", error);
        notificationStore.error("获取卡片失败", "请检查您的网络连接或权限");
    } finally {
        loading.value = false;
    }
};

// 过滤和排序卡片
const filteredCards = computed(() => {
    let result = [...cards.value];

    // 仅显示草稿
    if (showOnlyDrafts.value) {
        result = result.filter(card => !card.card_id);
    }

    // 排序
    result.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return sortByNewest.value ? dateB - dateA : dateA - dateB;
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

// 删除草稿
const deleteCard = async (uuid: string) => {
    if (confirm('确定要删除这个卡片吗？此操作不可撤销。')) {
        try {
            // 根据是否为草稿选择不同的删除路径
            const isConfirmed = cards.value.find(c => c.uuid === uuid)?.card_id;
            if (isConfirmed) {
                await userStore.axiosInstance.delete(`/cards/${uuid}`);
            } else {
                await draftStore.deleteDraft(uuid);
            }
            // 重新获取卡片列表以更新UI
            await fetchCards();
            notificationStore.success("删除成功", "卡片已成功删除");
        } catch (error) {
            console.error("Error deleting card:", error);
            notificationStore.error("删除失败", "请检查您的网络连接或权限");
        }
    }
};

// 更新卡片状态
const updateCardStatus = async (uuid: string, mode: 'CONFIRMED' | 'UNSET') => {
    try {
        await userStore.axiosInstance.patch(`/cards/${uuid}?mode=${mode}`);
        // 重新获取卡片列表以更新UI
        await fetchCards();
        notificationStore.success("状态更新成功", `卡片状态已更新为${mode === 'CONFIRMED' ? '已确认' : '草稿'}`);
        showStatusConfirm.value = false;
    } catch (error) {
        console.error("Error updating card status:", error);
        notificationStore.error("状态更新失败", "请检查您的网络连接或权限");
    }
};

// 确认查询
const searchCards = () => {
    if (phoneNumber.value) {
        var re = /^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$/;
        if (!re.test(phoneNumber.value)) {
            notificationStore.warning("格式错误", "请输入正确的手机号码");
            return;
        }
    }
    fetchCards();
};

// 显示预览
const previewCard = async (card: Card) => {
    selectedCard.value = card;
    loading.value = true;
    try {
        if (card.card_id) {
            // 已确认的卡片使用不同的API
            const response = await userStore.axiosInstance.get(`/cards/${card.uuid}/profile`);
            previewPreferences.value = response.data.preferences;
        } else {
            // 草稿使用草稿的API
            previewPreferences.value = await draftStore.fetchPreferences(card.uuid);
        }
        showPreview.value = true;
    } catch (error) {
        console.error("Error fetching preferences for preview:", error);
        notificationStore.error("获取预览失败", "无法获取卡片配置");
    } finally {
        loading.value = false;
    }
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    selectedCard.value = null;
};

// 更新确认状态
const showStatusDialog = (card: Card) => {
    selectedCard.value = card;
    showStatusConfirm.value = true;
};

// 格式化日期显示
const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
};

// 获取短ID用于显示
const getShortId = (uuid: string) => {
    return uuid.substring(0, 6);
};

// 订单状态显示逻辑
const getOrderStatus = (card: Card) => {
    if (card.user_id && card.card_id) return '已激活';
    return card.card_id ? '已确认' : '草稿';
};

const preferencesReadOnly = computed(() => {
    if (!previewPreferences.value) return null;
    return JSON.parse(JSON.stringify(previewPreferences.value));
});

// 初始加载
fetchCards();
</script>

<template>
    <!-- 预览弹窗 -->
    <div v-if="showPreview && previewPreferences"
        class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg w-full overflow-hidden" style="max-width: 30rem;">
            <div class="p-4 bg-blue-400 text-white flex justify-between items-center">
                <span class="font-bold text-nowrap">卡面预览 - 订单号: {{ getShortId(selectedCard!.uuid) }}</span>
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
                <span class="font-bold">更新订单状态 - {{ getShortId(selectedCard.uuid) }}</span>
            </div>
            <div class="p-6">
                <p class="mb-4">当前状态:
                    <span :class="{
                        'bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full font-bold': !selectedCard.card_id,
                        'bg-green-100 text-green-800 px-2 py-1 rounded-full font-bold': selectedCard.card_id
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
                        class="bg-yellow-500 text-white py-2 px-4 rounded hover:bg-yellow-600">
                        设为草稿
                    </button>
                    <button @click="updateCardStatus(selectedCard.uuid, 'CONFIRMED')"
                        class="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600">
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
                    <input v-model="phoneNumber" type="text" placeholder="按手机号查询..."
                        class="flex-1 p-2 border border-gray-300 rounded mr-2 w-full md:w-auto">
                    <button @click="searchCards"
                        class="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 whitespace-nowrap">
                        <svg xmlns="http://www.w3.org/2000/svg" class="inline h-5 w-5 mr-1" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                                clip-rule="evenodd" />
                        </svg>
                        查询
                    </button>
                </div>

                <div class="flex items-center space-x-4">
                    <label class="flex items-center cursor-pointer">
                        <input type="checkbox" v-model="showOnlyDrafts" class="form-checkbox h-5 w-5 text-blue-600">
                        <span class="ml-2 text-gray-700">仅显示草稿</span>
                    </label>

                    <div class="flex items-center">
                        <span class="mr-2 text-gray-700">排序:</span>
                        <button @click="sortByNewest = true"
                            :class="sortByNewest ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-gray-100 text-gray-800 border-gray-300'"
                            class="px-3 py-1 rounded-l border">
                            最新
                        </button>
                        <button @click="sortByNewest = false"
                            :class="!sortByNewest ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-gray-100 text-gray-800 border-gray-300'"
                            class="px-3 py-1 rounded-r border border-l-0">
                            最早
                        </button>
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center">
                <span class="text-gray-600">总计: {{ filteredCards.length }} 条记录</span>
                <button @click="fetchCards" class="text-blue-600 hover:text-blue-800">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- 卡片列表 -->
        <div v-if="loading" class="text-center py-10">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent">
            </div>
            <p class="mt-2 text-gray-600">加载中...</p>
        </div>

        <div v-else-if="groupedCards.length === 0" class="text-center py-10">
            <p class="text-gray-600">没有找到符合条件的卡片</p>
        </div>

        <div v-else>
            <div v-for="(group, index) in groupedCards" :key="group.phoneNumber" class="mb-8 group-container">
                <!-- 手机号码分组标题 -->
                <div class="group-header">
                    手机号码: {{ group.phoneNumber }} ({{ group.cards.length }}张卡片)
                </div>

                <div v-for="card in group.cards" :key="card.uuid"
                    class="bg-white shadow mb-1 overflow-hidden group-card">
                    <div class="border-b border-gray-200 bg-gray-50 px-4 py-3 flex justify-between items-center">
                        <div>
                            <span class="font-bold">订单号: {{ getShortId(card.uuid) }}</span>
                            <span :class="{
                                'ml-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs font-bold': !card.card_id && !card.user_id,
                                'ml-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-bold': card.card_id && !card.user_id,
                                'ml-2 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-bold': card.user_id && card.card_id
                            }">
                                {{ getOrderStatus(card) }}
                            </span>
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
                                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
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
                            <button @click="showStatusDialog(card)"
                                class="bg-amber-500 text-white py-2 px-4 rounded hover:bg-amber-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z"
                                        clip-rule="evenodd" />
                                </svg>
                                更新
                            </button>

                            <!-- 删除按钮 -->
                            <button @click="deleteCard(card.uuid)"
                                class="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path fill-rule="evenodd"
                                        d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                        clip-rule="evenodd" />
                                </svg>
                                删除
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
</style>

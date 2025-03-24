<script setup lang="ts">
import { useDraftStore } from '@/stores/draft';
import type { Card, Preference } from '@/types';
import { computed, onActivated, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import DXBaseView from '@/views/DXBaseView.vue';
import { useNotificationStore } from '@/stores/notification';
import { matchPhoneNumber, getShortUuid, formatDate, getOrderStatus } from '@/utils';
import Prompt from '@/components/widgets/Prompt.vue';

const props = defineProps<{
    phoneNumber?: string;
}>();

const draftStore = useDraftStore();
const notificationStore = useNotificationStore();

const drafts = ref<Card[]>([]);
const phoneNumber = ref(props.phoneNumber || "");
const selectedDraft = ref<Card | null>(null);
const previewPreferences = ref<Preference | null>(null);
const showPreview = ref(false);
const showDeleteConfirm = ref(false);
const draftToDelete = ref("");

const fetchDrafts = async () => {
    drafts.value = await draftStore.fetchDrafts(phoneNumber.value);
};

const deleteDraft = async (uuid: string) => {
    await draftStore.deleteDraft(uuid);
    await fetchDrafts();
    notificationStore.success("删除成功", "草稿已成功删除");
};

// 修改为显示确认对话框
const confirmDelete = (uuid: string) => {
    draftToDelete.value = uuid;
    showDeleteConfirm.value = true;
};

// 确认删除的处理函数
const handleConfirmDelete = () => {
    if (draftToDelete.value) {
        deleteDraft(draftToDelete.value);
        showDeleteConfirm.value = false;
        draftToDelete.value = "";
    }
};

// 取消删除的处理函数
const handleCancelDelete = () => {
    showDeleteConfirm.value = false;
    draftToDelete.value = "";
};

const searchDrafts = () => {
    if (matchPhoneNumber(phoneNumber.value)) fetchDrafts();
};

const previewDraft = async (draft: Card) => {
    selectedDraft.value = draft;
    previewPreferences.value = await draftStore.fetchPreferences(draft.uuid);
    showPreview.value = true;
};

const closePreview = () => {
    showPreview.value = false;
    selectedDraft.value = null;
};

const preferencesReadOnly = computed(() => {
    if (!previewPreferences.value) return null;
    return JSON.parse(JSON.stringify(previewPreferences.value));
});

onActivated(() => {
    if (phoneNumber.value) fetchDrafts();
});
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
                <span class="font-bold text-nowrap">卡面预览 - 订单号: {{ getShortUuid(selectedDraft!.uuid) }}</span>
            </div>
            <div class="p-4 flex flex-col items-center">
                <div class="flex flex-1 preview-radius w-full" style="max-width: 100vw; ">
                    <DXBaseView :preferences="preferencesReadOnly" />
                </div>
                <div class="mt-4 flex justify-end w-full">
                    <button @click="closePreview"
                        class="bg-gray-500 hover:bg-gray-600 text-white py-3 px-6 rounded-lg font-bold">
                        关闭
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- 我的订单部分 - 移除外框 -->
    <div class="w-full mb-6">
        <div class="w-full p-4 bg-gray-50 rounded-lg">
            <div class="flex flex-col items-center justify-center">
                <div class="flex justify-between items-center w-full mb-4">
                    <div class="flex flex-col p-2">
                        <span class="font-medium">手机号码</span>
                        <span class="text-gray-600" style="font-size: 12px;">号码仅用于跟踪和确认订单</span>
                    </div>
                    <div><input v-model="phoneNumber" class="shadow-sm"></div>
                </div>
                <div class="flex w-full flex-col sm:flex-row gap-3">
                    <button
                        class="bg-blue-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-600 shadow-md flex items-center transition-colors"
                        @click="searchDrafts">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                                clip-rule="evenodd" />
                        </svg>
                        查询订单
                    </button>
                    <RouterLink
                        class="bg-green-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-600 shadow-md flex items-center transition-colors"
                        :to="{ name: 'designer', state: { phoneNumber: phoneNumber } }">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                            fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                                clip-rule="evenodd" />
                        </svg>
                        创建订单
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>

    <!-- 查询结果部分 - 移除外框 -->
    <template v-if="drafts.length">
        <div class="w-full">
            <div class="w-full">
                <div class="grid gap-6">
                    <div v-for="draft in drafts" :key="draft.uuid"
                        class="border border-gray-200 rounded-lg p-5 hover:shadow-lg transition-shadow bg-white">
                        <div class="flex flex-col md:flex-row gap-4">
                            <!-- 左侧：订单信息 -->
                            <div class="flex-1">
                                <h3 class="text-lg font-bold mb-3">订单编号: {{ getShortUuid(draft.uuid) }}</h3>
                                <div class="space-y-3">
                                    <p class="text-gray-600">
                                        <span class="font-semibold">创建时间:</span> {{ formatDate(draft.created_at) }}
                                    </p>
                                    <p class="flex items-center">
                                        <span class="font-semibold mr-2">订单状态:</span>
                                        <span :class="{
                                            'bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full font-bold': !draft.card_id,
                                            'bg-green-100 text-green-800 px-3 py-1 rounded-full font-bold': draft.card_id
                                        }">
                                            {{ getOrderStatus(draft) }}
                                        </span>
                                    </p>
                                </div>
                                <div class="mt-5 flex flex-wrap gap-3">
                                    <!-- 预览按钮 -->
                                    <button @click="previewDraft(draft)"
                                        class="bg-purple-500 text-white py-3 px-6 rounded-lg hover:bg-purple-600 font-bold flex items-center shadow-md transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                            fill="currentColor">
                                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                            <path fill-rule="evenodd"
                                                d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        预览卡面
                                    </button>

                                    <!-- 编辑按钮 -->
                                    <RouterLink v-if="!draft.card_id"
                                        :to="{ name: 'designer', params: { uuid: draft.uuid } }"
                                        class="bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 font-bold flex items-center shadow-md transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                            fill="currentColor">
                                            <path
                                                d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                        </svg>
                                        编辑订单
                                    </RouterLink>

                                    <!-- 删除按钮 -->
                                    <button v-if="!draft.card_id" @click="confirmDelete(draft.uuid)"
                                        class="bg-red-500 text-white py-3 px-6 rounded-lg hover:bg-red-600 font-bold flex items-center shadow-md transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20"
                                            fill="currentColor">
                                            <path fill-rule="evenodd"
                                                d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                                clip-rule="evenodd" />
                                        </svg>
                                        删除订单
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>

<style scoped>
.preview-radius {
    border-radius: 16px;
    mask-image: radial-gradient(circle, white 100%, black 100%);
    -webkit-mask-image: -webkit-radial-gradient(circle, white 100%, black 100%);
    overflow: hidden;
}

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

/* 移动设备适配 */
@media (max-width: 640px) {
    .flex-col-mobile {
        flex-direction: column;
    }

    button,
    a.bg-blue-500,
    a.bg-green-500,
    a.bg-red-500,
    a.bg-purple-500 {
        width: 100%;
        justify-content: center;
    }
}
</style>

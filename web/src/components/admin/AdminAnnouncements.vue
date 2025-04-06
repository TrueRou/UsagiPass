<script setup lang="ts">
import { useAnnouncementStore, type Announcement } from '@/stores/announcement';
import { useNotificationStore } from '@/stores/notification';
import { computed, ref, onMounted, watch } from 'vue';
import Prompt from '@/components/widgets/Prompt.vue';

const announcementStore = useAnnouncementStore();
const notificationStore = useNotificationStore();

const announcements = ref<Announcement[]>([]);
const isLoading = ref(false);

// 编辑公告相关状态
const editingAnnouncement = ref<Announcement | null>(null);
const newTitle = ref('');
const newContent = ref('');

// 显示编辑对话框
const showEditDialog = ref(false);

// 删除确认
const showDeleteConfirm = ref(false);
const announcementToDelete = ref<number | null>(null);

// 预览相关
const previewMode = ref(false);
const previewContent = computed(() => {
    if (!newContent.value) return '';
    return announcementStore.renderMarkdown(newContent.value);
});

const showCreateDialog = ref(false);

// 筛选相关
const titleFilter = ref('');
const statusFilter = ref<'all' | boolean | null>('all');
const dateFilter = ref<'all' | '3days' | 'week' | 'month'>('all');

const fetchData = async () => {
    isLoading.value = true;
    try {
        announcements.value = await announcementStore.fetchAnnouncements();
    } finally {
        isLoading.value = false;
    }
};

const handleCreateAnnouncement = async () => {
    if (!newTitle.value.trim()) {
        notificationStore.warning('标题不能为空', '请输入公告标题');
        return;
    }

    if (!newContent.value.trim()) {
        notificationStore.warning('内容不能为空', '请输入公告内容');
        return;
    }

    isLoading.value = true;
    try {
        await announcementStore.createAnnouncement(newTitle.value, newContent.value);
        notificationStore.success('创建成功', '公告已成功创建');
        resetForm();
        showCreateDialog.value = false;
        await fetchData();
    } finally {
        isLoading.value = false;
    }
};

const startEdit = (announcement: Announcement) => {
    editingAnnouncement.value = announcement;
    newTitle.value = announcement.title;
    newContent.value = announcement.content;
    showEditDialog.value = true;
};

const handleUpdateAnnouncement = async () => {
    if (!editingAnnouncement.value) return;

    if (!newTitle.value.trim()) {
        notificationStore.warning('标题不能为空', '请输入公告标题');
        return;
    }

    if (!newContent.value.trim()) {
        notificationStore.warning('内容不能为空', '请输入公告内容');
        return;
    }

    isLoading.value = true;
    try {
        await announcementStore.updateAnnouncement(editingAnnouncement.value.id, {
            title: newTitle.value,
            content: newContent.value
        });
        notificationStore.success('更新成功', '公告已成功更新');
        resetForm();
        showEditDialog.value = false;
        await fetchData();
    } finally {
        isLoading.value = false;
    }
};

const confirmDelete = async () => {
    if (announcementToDelete.value === null) return;

    isLoading.value = true;
    try {
        await announcementStore.deleteAnnouncement(announcementToDelete.value);
        notificationStore.success('删除成功', '公告已成功删除');
        showDeleteConfirm.value = false;
        announcementToDelete.value = null;
        await fetchData();
    } finally {
        isLoading.value = false;
    }
};

const showDeleteDialog = (id: number) => {
    announcementToDelete.value = id;
    showDeleteConfirm.value = true;
};

const cancelDelete = () => {
    showDeleteConfirm.value = false;
    announcementToDelete.value = null;
};

const resetForm = () => {
    editingAnnouncement.value = null;
    newTitle.value = '';
    newContent.value = '';
    previewMode.value = false;
};

const toggleAnnouncementStatus = async (announcement: Announcement) => {
    isLoading.value = true;
    try {
        // 存储当前状态以便正确显示消息
        const currentStatus = announcement.is_active;
        await announcementStore.updateAnnouncement(announcement.id, {
            is_active: !currentStatus
        });
        notificationStore.success('更新成功', `公告已${currentStatus ? '禁用' : '启用'}`);
        await fetchData();
    } finally {
        isLoading.value = false;
    }
};

const openCreateDialog = () => {
    resetForm();
    showCreateDialog.value = true;
};

// 格式化日期
const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// 新增：格式化精确日期
const formatDateDetailed = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

// 新增：截取内容预览
const getContentPreview = (content: string, maxLength: number = 100) => {
    const plainText = content.replace(/[#*`_~]/g, '');
    return plainText.length > maxLength
        ? plainText.slice(0, maxLength) + '...'
        : plainText;
};

// 新增：根据日期筛选
const filteredAnnouncements = computed(() => {
    let result = [...announcements.value];

    // 按标题筛选
    if (titleFilter.value) {
        result = result.filter(announcement =>
            announcement.title.toLowerCase().includes(titleFilter.value.toLowerCase())
        );
    }

    // 按状态筛选
    if (statusFilter.value !== 'all') {
        result = result.filter(announcement =>
            announcement.is_active === (statusFilter.value === true)
        );
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

        result = result.filter(announcement => new Date(announcement.created_at) >= startDate);
    }

    // 默认按创建时间倒序排序
    result.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
    });

    return result;
});

onMounted(fetchData);
</script>

<template>
    <div class="w-full p-4">
        <!-- 删除确认对话框 -->
        <Prompt :show="showDeleteConfirm" text="确定要删除这条公告吗？此操作无法撤销。" @confirm="confirmDelete" @cancel="cancelDelete" />

        <!-- 创建公告对话框 -->
        <Transition name="prompt-fade">
            <div v-if="showCreateDialog"
                class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-30"
                @click.self="showCreateDialog = false">
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl mx-4 transform transition-all">
                    <div class="p-5 sm:p-6">
                        <h3 class="text-lg sm:text-xl font-medium text-gray-900 dark:text-white mb-4">
                            创建新公告
                        </h3>

                        <div class="space-y-4">
                            <div>
                                <label for="dialog-announcement-title"
                                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    公告标题
                                </label>
                                <input id="dialog-announcement-title" v-model="newTitle" type="text"
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    placeholder="输入公告标题" />
                            </div>

                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <label for="dialog-announcement-content"
                                        class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                        公告内容 (支持Markdown格式)
                                    </label>
                                    <button @click="previewMode = !previewMode"
                                        class="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors">
                                        {{ previewMode ? '编辑模式' : '预览模式' }}
                                    </button>
                                </div>

                                <textarea v-if="!previewMode" id="dialog-announcement-content" v-model="newContent"
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white h-48"
                                    placeholder="输入公告内容，支持Markdown格式"></textarea>

                                <div v-else
                                    class="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white h-48 overflow-y-auto prose dark:prose-invert max-w-none">
                                    <div v-if="newContent" v-html="previewContent"></div>
                                    <div v-else class="text-gray-400 dark:text-gray-500 italic">预览区域为空，请输入内容</div>
                                </div>
                            </div>

                            <div class="flex justify-end space-x-3 mt-6">
                                <button @click="showCreateDialog = false"
                                    class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors">
                                    取消
                                </button>
                                <button @click="handleCreateAnnouncement" :disabled="isLoading"
                                    class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                                    {{ isLoading ? '创建中...' : '创建公告' }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- 编辑公告对话框 -->
        <Transition name="prompt-fade">
            <div v-if="showEditDialog"
                class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-30"
                @click.self="showEditDialog = false">
                <div
                    class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl mx-4 transform transition-all">
                    <div class="p-5 sm:p-6">
                        <h3 class="text-lg sm:text-xl font-medium text-gray-900 dark:text-white mb-4">
                            编辑公告
                        </h3>

                        <div class="space-y-4">
                            <div>
                                <label for="edit-announcement-title"
                                    class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    公告标题
                                </label>
                                <input id="edit-announcement-title" v-model="newTitle" type="text"
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    placeholder="输入公告标题" />
                            </div>

                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <label for="edit-announcement-content"
                                        class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                        公告内容 (支持Markdown格式)
                                    </label>
                                    <button @click="previewMode = !previewMode"
                                        class="px-2 py-1 text-xs bg-gray-200 dark:bg-gray-600 rounded hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors">
                                        {{ previewMode ? '编辑模式' : '预览模式' }}
                                    </button>
                                </div>

                                <textarea v-if="!previewMode" id="edit-announcement-content" v-model="newContent"
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white h-48"
                                    placeholder="输入公告内容，支持Markdown格式"></textarea>

                                <div v-else
                                    class="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white h-48 overflow-y-auto prose dark:prose-invert max-w-none">
                                    <div v-if="newContent" v-html="previewContent"></div>
                                    <div v-else class="text-gray-400 dark:text-gray-500 italic">预览区域为空，请输入内容</div>
                                </div>
                            </div>

                            <div class="flex justify-end space-x-3 mt-6">
                                <button @click="showEditDialog = false"
                                    class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors">
                                    取消
                                </button>
                                <button @click="handleUpdateAnnouncement" :disabled="isLoading"
                                    class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                                    {{ isLoading ? '更新中...' : '更新公告' }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- 公告管理界面 -->
        <div class="bg-white dark:bg-gray-800">
            <!-- 搜索和筛选区域 -->
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="flex flex-1 items-center">
                    <input v-model="titleFilter" type="text" placeholder="按标题过滤..."
                        class="flex-1 p-2 border border-gray-300 rounded mr-2 w-full md:w-auto">
                </div>

                <div class="flex items-center gap-4 flex-wrap">
                    <!-- 按状态筛选 -->
                    <div class="flex flex-wrap items-center gap-2">
                        <div class="flex border border-gray-300 rounded-md overflow-hidden">
                            <button @click="statusFilter = 'all';"
                                :class="{ 'bg-blue-500 text-white': statusFilter === 'all', 'bg-gray-100 hover:bg-gray-200': statusFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium">
                                全部
                            </button>
                            <button @click="statusFilter = true;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === true, 'bg-gray-100 hover:bg-gray-200': statusFilter !== true }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                已启用
                            </button>
                            <button @click="statusFilter = false;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === false, 'bg-gray-100 hover:bg-gray-200': statusFilter !== false }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                已禁用
                            </button>
                        </div>
                    </div>

                    <!-- 按时间筛选 -->
                    <div class="flex flex-wrap items-center gap-2">
                        <div class="flex border border-gray-300 rounded-md overflow-hidden">
                            <button @click="dateFilter = 'all';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'all', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium">
                                全部
                            </button>
                            <button @click="dateFilter = '3days';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === '3days', 'bg-gray-100 hover:bg-gray-200': dateFilter !== '3days' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                三日内
                            </button>
                            <button @click="dateFilter = 'week';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'week', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'week' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                一周内
                            </button>
                            <button @click="dateFilter = 'month';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'month', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'month' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300">
                                一月内
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                <div class="flex items-center justify-between h-8 my-2 w-full">
                    <span class="text-gray-600">总计: {{ filteredAnnouncements.length }} 条记录</span>
                    <div>
                        <button @click="openCreateDialog" class="text-green-600 hover:text-green-700">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 4v16m8-8H4" />
                            </svg>
                        </button>
                        <button @click="fetchData" :disabled="isLoading"
                            class="inline-flex items-center p-2 text-blue-600 rounded-lg hover:bg-gray-100 dark:text-blue-400 dark:hover:bg-gray-700">
                            <svg v-if="isLoading" class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg"
                                fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4">
                                </circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 现有公告列表 -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden">
            <div v-if="filteredAnnouncements.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p>暂无公告</p>
            </div>
            <template v-else>
                <!-- 移动端卡片视图 -->
                <div class="block md:hidden">
                    <div class="relative">
                        <div v-for="announcement in filteredAnnouncements" :key="announcement.id"
                            class="announcement-card"
                            :class="{ 'bg-gray-50 dark:bg-gray-700/50': !announcement.is_active }">
                            <div class="border-b dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800/50">
                                <div class="flex justify-between items-start">
                                    <div class="flex-1">
                                        <div class="flex items-center gap-2 mb-2">
                                            <h3 class="text-md font-medium text-gray-900 dark:text-white">
                                                {{ announcement.title }}
                                            </h3>
                                            <span
                                                :class="announcement.is_active ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'"
                                                class="px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full">
                                                {{ announcement.is_active ? '已启用' : '已禁用' }}
                                            </span>
                                        </div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400 mb-3 flex items-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                            {{ formatDate(announcement.created_at) }}
                                        </div>
                                        <div class="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-3">
                                            {{ getContentPreview(announcement.content) }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="flex space-x-3 p-3">
                                <button @click="startEdit(announcement)"
                                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                        viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                    编辑
                                </button>
                                <button @click="toggleAnnouncementStatus(announcement)"
                                    :class="announcement.is_active ? 'text-yellow-600 hover:text-yellow-900 dark:text-yellow-400 dark:hover:text-yellow-300' : 'text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300'"
                                    class="text-sm flex items-center">
                                    <svg v-if="announcement.is_active" xmlns="http://www.w3.org/2000/svg"
                                        class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                    </svg>
                                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                        viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    {{ announcement.is_active ? '禁用' : '启用' }}
                                </button>
                                <button @click="showDeleteDialog(announcement.id)"
                                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                        viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    删除
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 桌面端表格视图 -->
                <div class="hidden md:block overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead class="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    标题
                                </th>
                                <th scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    内容预览
                                </th>
                                <th scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    创建时间
                                </th>
                                <th scope="col"
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    状态
                                </th>
                                <th scope="col"
                                    class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                    操作
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                            <tr v-for="announcement in filteredAnnouncements" :key="announcement.id"
                                :class="{ 'bg-gray-50 dark:bg-gray-700/50': !announcement.is_active }">
                                <td class="px-6 py-4">
                                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                                        {{ announcement.title }}
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="text-sm text-gray-500 dark:text-gray-400 w-64 truncate">
                                        {{ getContentPreview(announcement.content, 50) }}
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="text-sm text-gray-500 dark:text-gray-400">
                                        {{ formatDate(announcement.created_at) }}
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span
                                        :class="announcement.is_active ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'"
                                        class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                                        {{ announcement.is_active ? '已启用' : '已禁用' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <div class="flex justify-end space-x-2">
                                        <button @click="startEdit(announcement)"
                                            class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 flex items-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                            </svg>
                                            编辑
                                        </button>
                                        <button @click="toggleAnnouncementStatus(announcement)"
                                            :class="announcement.is_active ? 'text-yellow-600 hover:text-yellow-900 dark:text-yellow-400 dark:hover:text-yellow-300' : 'text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300'"
                                            class="flex items-center">
                                            <svg v-if="announcement.is_active" xmlns="http://www.w3.org/2000/svg"
                                                class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24"
                                                stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                            </svg>
                                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1"
                                                fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            {{ announcement.is_active ? '禁用' : '启用' }}
                                        </button>
                                        <button @click="showDeleteDialog(announcement.id)"
                                            class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 flex items-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                                viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                            删除
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </template>
        </div>
    </div>
</template>

<style scoped>
:deep(.prose) {
    max-width: 100%;
}

:deep(.prose a) {
    color: #3b82f6;
    text-decoration: underline;
}

:deep(.prose a:hover) {
    color: #2563eb;
}

:deep(.prose img) {
    max-width: 100%;
    height: auto;
    border-radius: 0.375rem;
}

:deep(.prose pre) {
    background-color: #f3f4f6;
    border-radius: 0.375rem;
    padding: 1rem;
    overflow-x: auto;
}

:deep(.prose code) {
    background-color: #f3f4f6;
    padding: 0.2rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
}

@media (prefers-color-scheme: dark) {
    :deep(.prose pre) {
        background-color: #374151;
    }

    :deep(.prose code) {
        background-color: #374151;
    }
}

.announcement-card {
    border-radius: 0.375rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    background-color: white;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

@media (prefers-color-scheme: dark) {
    .announcement-card {
        background-color: #1f2937;
        border-color: #374151;
    }
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

/* 放大按钮 */
button {
    transition: transform 0.1s ease-in-out;
}

button:active:not(:disabled) {
    transform: scale(0.97);
}
</style>
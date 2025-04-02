<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { formatDateDetailed, getShortUuid } from '@/utils/formatUtils';
import type { Task } from '@/types';
import { TaskStatus, TaskStatusMap } from '@/types';

const userStore = useUserStore();
const notificationStore = useNotificationStore();

const tasks = ref<Task[]>([]);
const isLoading = ref(false);
const isDownloading = ref(false);
const isDeleting = ref(false);
const showDeleteConfirm = ref(false);
const taskToDelete = ref<string | null>(null);
const dateFilter = ref('all');
const statusFilter = ref<'all' | TaskStatus>('all');

const fetchTasks = async () => {
    try {
        isLoading.value = true;
        const response = await userStore.axiosInstance.get('/tasks');
        tasks.value = response.data;
    } catch (error: any) {
        notificationStore.error("获取任务失败", error.response?.data?.detail || "未知错误");
    } finally {
        isLoading.value = false;
    }
};

const downloadTaskResult = async (taskId: string) => {
    try {
        isDownloading.value = true;
        notificationStore.info("准备下载", "正在准备下载任务结果...");

        const response = await userStore.axiosInstance.get(`/tasks/${taskId}/download`, {
            responseType: 'blob'
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `task_${taskId}.zip`;
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        notificationStore.success("下载成功", "已成功下载任务结果");
    } catch (error: any) {
        notificationStore.error("下载失败", error.response?.data?.detail || "未知错误");
    } finally {
        isDownloading.value = false;
    }
};

const deleteTask = async (taskId: string) => {
    try {
        isDeleting.value = true;

        await userStore.axiosInstance.delete(`/tasks/${taskId}`);

        notificationStore.success("删除成功", "任务已成功删除");
        await fetchTasks();
        showDeleteConfirm.value = false;
        taskToDelete.value = null;
    } catch (error: any) {
        notificationStore.error("删除失败", error.response?.data?.detail || "未知错误");
    } finally {
        isDeleting.value = false;
    }
};

const confirmDelete = (taskId: string) => {
    taskToDelete.value = taskId;
    showDeleteConfirm.value = true;
};

const cancelDelete = () => {
    showDeleteConfirm.value = false;
    taskToDelete.value = null;
};

const filteredTasks = computed(() => {
    let result = [...tasks.value];

    // 按状态筛选
    if (statusFilter.value !== 'all') {
        result = result.filter(task => task.status === statusFilter.value);
    }

    // 按时间段筛选
    if (dateFilter.value !== 'all') {
        const now = new Date();
        let startDate;

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

        result = result.filter(task => new Date(task.created_at) >= startDate);
    }

    // 默认排序（最新的在前面）
    result.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
    });

    return result;
});

const refreshTasks = async () => {
    await fetchTasks();
};


let refreshInterval: any = null;

onMounted(() => {
    fetchTasks();
    refreshInterval = setInterval(() => {
        fetchTasks();
    }, 5000);
});

onUnmounted(() => {
    clearInterval(refreshInterval);
});
</script>

<template>
    <div class="w-full p-4">
        <!-- 删除确认对话框 -->
        <div v-if="showDeleteConfirm"
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 max-w-sm mx-4 w-full">
                <h3 class="text-lg font-bold mb-4">确认删除</h3>
                <p class="mb-6">确定要删除此任务吗？</p>
                <div class="flex justify-end gap-3">
                    <button @click="cancelDelete" class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400 text-gray-800">
                        取消
                    </button>
                    <button @click="deleteTask(taskToDelete!)" :disabled="isDeleting"
                        class="px-4 py-2 bg-red-600 rounded hover:bg-red-700 text-white flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
                        <svg v-if="isDeleting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                        </svg>
                        删除
                    </button>
                </div>
            </div>
        </div>

        <!-- 搜索和筛选区域 -->
        <div class="flex flex-col bg-white p-4 py-0">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full sm:w-auto">
                    <!-- 按任务状态筛选 -->
                    <div class="flex flex-col w-full sm:w-auto">
                        <div class="flex flex-wrap border border-gray-300 rounded-md overflow-hidden w-full sm:w-auto">
                            <button @click="statusFilter = 'all';"
                                :class="{ 'bg-blue-500 text-white': statusFilter === 'all', 'bg-gray-100 hover:bg-gray-200': statusFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium flex-1 sm:flex-none">
                                全部
                            </button>
                            <button @click="statusFilter = TaskStatus.PENDING;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === TaskStatus.PENDING, 'bg-gray-100 hover:bg-gray-200': statusFilter !== TaskStatus.PENDING }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                等待中
                            </button>
                            <button @click="statusFilter = TaskStatus.RUNNING;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === TaskStatus.RUNNING, 'bg-gray-100 hover:bg-gray-200': statusFilter !== TaskStatus.RUNNING }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                处理中
                            </button>
                            <button @click="statusFilter = TaskStatus.COMPLETED;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === TaskStatus.COMPLETED, 'bg-gray-100 hover:bg-gray-200': statusFilter !== TaskStatus.COMPLETED }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                已完成
                            </button>
                            <button @click="statusFilter = TaskStatus.FAILED;"
                                :class="{ 'bg-blue-500 text-white': statusFilter === TaskStatus.FAILED, 'bg-gray-100 hover:bg-gray-200': statusFilter !== TaskStatus.FAILED }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                失败
                            </button>
                        </div>
                    </div>

                    <!-- 按时间筛选 -->
                    <div class="flex flex-col w-full sm:w-auto">
                        <div class="flex flex-wrap border border-gray-300 rounded-md overflow-hidden w-full sm:w-auto">
                            <button @click="dateFilter = 'all';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'all', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'all' }"
                                class="px-3 py-1.5 text-sm font-medium flex-1 sm:flex-none">
                                全部
                            </button>
                            <button @click="dateFilter = '3days';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === '3days', 'bg-gray-100 hover:bg-gray-200': dateFilter !== '3days' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                三日内
                            </button>
                            <button @click="dateFilter = 'week';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'week', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'week' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                一周内
                            </button>
                            <button @click="dateFilter = 'month';"
                                :class="{ 'bg-blue-500 text-white': dateFilter === 'month', 'bg-gray-100 hover:bg-gray-200': dateFilter !== 'month' }"
                                class="px-3 py-1.5 text-sm font-medium border-l border-gray-300 flex-1 sm:flex-none">
                                一月内
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center h-8">
                <div class="flex items-center">
                    <span class="text-gray-600 mr-4">总计: {{ filteredTasks.length }} 条记录</span>
                </div>
                <div class="flex items-center gap-2">
                    <!-- 刷新按钮 -->
                    <button @click="refreshTasks" class="text-blue-600 hover:text-blue-800" :disabled="isLoading">
                        <svg v-if="isLoading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg"
                            fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                            </circle>
                            <path class="opacity-75" fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                            </path>
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- 任务列表 -->
        <div v-if="filteredTasks.length === 0" class="text-center py-10">
            <p class="text-gray-600">没有找到符合条件的任务</p>
        </div>

        <div v-else class="mt-4">
            <!-- 桌面端表格视图 -->
            <div class="bg-white shadow rounded-lg overflow-hidden hidden md:block">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                任务ID
                            </th>
                            <th scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                任务类型
                            </th>
                            <th scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                创建时间
                            </th>
                            <th scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                状态
                            </th>
                            <th scope="col"
                                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                操作
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="task in filteredTasks" :key="task.id">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {{ getShortUuid(task.id) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ task.task_type }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ formatDateDetailed(task.created_at) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <span :class="TaskStatusMap[task.status].color">
                                    {{ TaskStatusMap[task.status].tag }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <div class="flex items-center space-x-2">
                                    <button v-if="task.status === TaskStatus.COMPLETED"
                                        @click="downloadTaskResult(task.id)" :disabled="isDownloading"
                                        class="text-white bg-blue-600 hover:bg-blue-700 py-1.5 px-3 rounded text-sm font-medium flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
                                        <svg v-if="isDownloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                                stroke-width="4">
                                            </circle>
                                            <path class="opacity-75" fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                            </path>
                                        </svg>
                                        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 3 0 003 3h10a3 3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        下载
                                    </button>
                                    <button v-if="task.status === TaskStatus.COMPLETED" @click="confirmDelete(task.id)"
                                        class="text-white bg-red-600 hover:bg-red-700 py-1.5 px-3 rounded text-sm font-medium flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                            viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                        删除
                                    </button>
                                    <span v-else-if="task.status === TaskStatus.FAILED"
                                        class="text-red-500">任务失败，无法下载</span>
                                    <span v-else class="text-gray-500">等待任务完成</span>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- 移动端卡片视图 -->
            <div class="grid grid-cols-1 gap-4 md:hidden">
                <div v-for="task in filteredTasks" :key="task.id"
                    class="bg-white border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div class="flex justify-between items-start mb-3">
                        <div class="flex flex-col">
                            <div class="text-sm font-medium text-gray-900">ID: {{ getShortUuid(task.id) }}</div>
                            <div class="text-sm text-gray-500">{{ task.task_type }}</div>
                        </div>
                        <span :class="TaskStatusMap[task.status].color">
                            {{ TaskStatusMap[task.status].tag }}
                        </span>
                    </div>
                    <div class="text-xs text-gray-500 mb-3">
                        创建时间: {{ formatDateDetailed(task.created_at) }}
                    </div>
                    <div class="mt-3">
                        <div class="flex flex-col space-y-2">
                            <button v-if="task.status === TaskStatus.COMPLETED" @click="downloadTaskResult(task.id)"
                                :disabled="isDownloading"
                                class="w-full text-white bg-blue-600 hover:bg-blue-700 py-2 px-3 rounded text-sm font-medium flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                                <svg v-if="isDownloading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4">
                                    </circle>
                                    <path class="opacity-75" fill="currentColor"
                                        d="M4 12a8 8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                    </path>
                                </svg>
                                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                    viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M4 16v1a3 3 3 0 003 3h10a3 3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                下载结果
                            </button>
                            <button v-if="task.status === TaskStatus.COMPLETED" @click="confirmDelete(task.id)"
                                class="w-full text-white bg-red-600 hover:bg-red-700 py-2 px-3 rounded text-sm font-medium flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none"
                                    viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                删除任务
                            </button>
                            <div v-else-if="task.status === TaskStatus.FAILED" class="text-red-500 text-center py-2">
                                任务失败，无法下载</div>
                            <div v-else class="text-gray-500 text-center py-2">等待任务完成</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 表格样式优化 */
table {
    border-collapse: separate;
    border-spacing: 0;
}

th {
    font-weight: 600;
    text-align: left;
    background-color: #f9fafb;
}

th,
td {
    padding: 0.75rem 1rem;
    vertical-align: middle;
}

tr:hover {
    background-color: #f9fafb;
}

/* 按钮和加载状态样式 */
button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

.animate-spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

/* 移动端响应式调整 */
@media (max-width: 640px) {
    .px-6 {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .py-4 {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
}
</style>

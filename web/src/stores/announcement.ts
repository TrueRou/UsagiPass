import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useUserStore } from './user';
import { useNotificationStore } from './notification';
import { markRaw } from 'vue';
import MarkdownIt from 'markdown-it';

// 创建一个markdownit解析器实例
const md = markRaw(new MarkdownIt({
    html: false,  // 禁用HTML标签
    linkify: true, // 将URL自动转换为链接
    typographer: true, // 启用一些语言中立的替换和引号美化
    breaks: true, // 转换换行符为 <br>
}));

export interface Announcement {
    id: number;
    title: string;
    content: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    is_read: boolean;
}

export const useAnnouncementStore = defineStore('announcement', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    const announcements = ref<Announcement[]>([]);
    const unreadAnnouncements = ref<Announcement[]>([]);
    const currentAnnouncement = ref<Announcement | null>(null);
    const showAnnouncementModal = ref(false);

    const fetchAnnouncements = async () => {
        try {
            const response = await userStore.axiosInstance.get('/announcements');
            announcements.value = response.data;
            updateUnreadAnnouncements();
            return announcements.value;
        } catch (error: any) {
            notificationStore.error('获取公告失败', error.response?.data?.detail || '未知错误');
            return [];
        }
    };

    const fetchAnnouncement = async (id: number) => {
        try {
            const response = await userStore.axiosInstance.get(`/announcements/${id}`);
            const announcement = response.data;
            return announcement;
        } catch (error: any) {
            notificationStore.error('获取公告失败', error.response?.data?.detail || '未知错误');
            return null;
        }
    };

    const createAnnouncement = async (title: string, content: string, isActive = true) => {
        try {
            const response = await userStore.axiosInstance.post('/announcements', {
                title,
                content,
                is_active: isActive
            });
            await fetchAnnouncements();
            return response.data;
        } catch (error: any) {
            notificationStore.error('创建公告失败', error.response?.data?.detail || '未知错误');
            return null;
        }
    };

    const updateAnnouncement = async (id: number, data: Partial<Announcement>) => {
        try {
            const response = await userStore.axiosInstance.patch(`/announcements/${id}`, data);
            await fetchAnnouncements();
            return response.data;
        } catch (error: any) {
            notificationStore.error('更新公告失败', error.response?.data?.detail || '未知错误');
            return null;
        }
    };

    const deleteAnnouncement = async (id: number) => {
        try {
            await userStore.axiosInstance.delete(`/announcements/${id}`);
            await fetchAnnouncements();
            return true;
        } catch (error: any) {
            notificationStore.error('删除公告失败', error.response?.data?.detail || '未知错误');
            return false;
        }
    };

    const markAsRead = async (id: number) => {
        try {
            await userStore.axiosInstance.post(`/announcements/${id}/read`);
            const index = announcements.value.findIndex(a => a.id === id);
            if (index !== -1) {
                announcements.value[index].is_read = true;
            }
            updateUnreadAnnouncements();
            return true;
        } catch (error: any) {
            notificationStore.error('标记公告已读失败', error.response?.data?.detail || '未知错误');
            return false;
        }
    };

    const updateUnreadAnnouncements = () => {
        unreadAnnouncements.value = announcements.value.filter(a => !a.is_read && a.is_active);
    };

    const showNextUnreadAnnouncement = () => {
        if (unreadAnnouncements.value.length > 0) {
            currentAnnouncement.value = unreadAnnouncements.value[0];
            showAnnouncementModal.value = true;
            return true;
        }
        return false;
    };

    const handleCurrentAnnouncementRead = async (mark: boolean = true) => {
        if (currentAnnouncement.value) {
            if (mark) await markAsRead(currentAnnouncement.value.id);
            showAnnouncementModal.value = false;
            return showNextUnreadAnnouncement();
        }
        return false;
    };

    const renderMarkdown = (content: string) => {
        return md.render(content);
    };

    const initAnnouncements = async () => {
        if (userStore.isSignedIn) {
            await fetchAnnouncements();
            showNextUnreadAnnouncement();
        }
    };

    return {
        announcements,
        unreadAnnouncements,
        currentAnnouncement,
        showAnnouncementModal,
        fetchAnnouncements,
        fetchAnnouncement,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
        markAsRead,
        showNextUnreadAnnouncement,
        handleCurrentAnnouncementRead,
        renderMarkdown,
        initAnnouncements
    };
});
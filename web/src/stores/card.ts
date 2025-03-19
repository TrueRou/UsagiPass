import { defineStore } from "pinia"
import { useUserStore } from "./user";
import type { CardProfile } from "@/types";
import { useNotificationStore } from "./notification";

export const useCardStore = defineStore('card', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    async function fetchCard(uuid: string): Promise<CardProfile> {
        try {
            const response = await userStore.axiosInstance.get(`/cards/${uuid}/profile`)
            return response.data
        } catch (error) {
            notificationStore.error("获取卡片失败", `无法获取卡片信息，请联系开发者\n卡片UUID: ${uuid}`)
            throw error
        }
    }

    async function activateCard(uuid: string, activationCode: string) {
        try {
            await userStore.axiosInstance.post(`/cards/${uuid}/accounts?qrcode=${activationCode}`);
        } catch (error: any) {
            notificationStore.error("激活失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function updateCardPreferences(uuid: string, preferences: any) {
        try {
            await userStore.axiosInstance.patch(`/cards/${uuid}/preference`, preferences);
        } catch (error: any) {
            notificationStore.error("保存失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    return { fetchCard, activateCard, updateCardPreferences }
})
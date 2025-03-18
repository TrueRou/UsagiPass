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

    return { fetchCard }
})
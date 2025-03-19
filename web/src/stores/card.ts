import { defineStore } from "pinia"
import { useUserStore } from "./user";
import type { CardProfile } from "@/types";
import { useNotificationStore } from "./notification";
import { ref } from "vue";

export const useCardStore = defineStore('card', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    const cardUUID = ref<string | null>(history.state.cardUUID || null);
    const cardProfile = ref<CardProfile | null>(null);

    async function refreshCard(uuid?: string) {
        if (!cardUUID.value && !uuid) {
            notificationStore.error("获取卡片失败", "卡片 UUID 未提供")
            return Promise.reject("卡片 UUID 未提供")
        }
        try {
            cardUUID.value = uuid || cardUUID.value
            cardProfile.value = (await userStore.axiosInstance.get(`/cards/${cardUUID.value}/profile`)).data
        } catch (error) {
            notificationStore.error("获取卡片失败", `无法获取卡片信息，请联系开发者\n卡片UUID: ${uuid}`)
            throw error
        }
    }

    async function activateCard(activationCode: string) {
        try {
            await userStore.axiosInstance.post(`/cards/${cardUUID.value}/accounts?qrcode=${activationCode}`);
        } catch (error: any) {
            notificationStore.error("激活失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function patchPreferences() {
        try {
            await userStore.axiosInstance.patch(`/cards/${cardUUID.value}/preference`, cardProfile.value?.preferences);
        } catch (error: any) {
            notificationStore.error("保存失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    return { refreshCard, activateCard, patchPreferences, cardUUID, cardProfile }
})
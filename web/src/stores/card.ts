import { ref } from "vue";
import { defineStore } from "pinia"
import { useUserStore } from "./user";
import { useNotificationStore } from "./notification";
import type { CardPreference, CardUser } from "@/types";

export const useCardStore = defineStore('card', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    const cardUUID = ref<string | null>(history.state.cardUUID || null);
    const cardPreference = ref<CardPreference | null>(null);
    const cardAccount = ref<CardUser | null>(null);

    async function refreshCard(uuid?: string) {
        if (!cardUUID.value && !uuid) {
            notificationStore.error("获取卡片失败", "卡片 UUID 未提供")
            return Promise.reject("卡片 UUID 未提供")
        }
        try {
            cardUUID.value = uuid || cardUUID.value
            cardPreference.value = (await userStore.axiosInstance.get(`/cards/${cardUUID.value}/preference`)).data
            userStore.axiosInstance.get(`/cards/${cardUUID.value}/accounts`).then(resp => cardAccount.value = resp.data).catch(() => cardAccount.value = null)
        } catch (error) {
            notificationStore.error("获取卡片失败", `无法获取卡片信息，请联系开发者\n卡片UUID: ${uuid}`)
            throw error
        }
    }

    async function createAccount(activationCode: string) {
        try {
            await userStore.axiosInstance.post(`/cards/${cardUUID.value}/accounts?qrcode=${activationCode}`);
        } catch (error: any) {
            notificationStore.error("激活失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function patchPreferences(uuid?: string, preference?: CardPreference) {
        try {
            uuid = uuid ?? cardUUID.value!;
            preference = preference ?? cardPreference.value!;
            await userStore.axiosInstance.patch(`/cards/${uuid}/preference`, preference);
        } catch (error: any) {
            notificationStore.error("保存失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function createCard() {
        try {
            const resp = await userStore.axiosInstance.post("/cards");
            return resp.data;
        } catch (error: any) {
            notificationStore.error("创建失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    return { refreshCard, createAccount, createCard, patchPreferences, cardUUID, cardPreference, cardAccount }
})
import { ref } from "vue";
import { defineStore } from "pinia"
import { useUserStore } from "./user";
import { useNotificationStore } from "./notification";
import type { Preference, CardProfile, CardScoreUpdateResult } from "@/types";

export const useCardStore = defineStore('card', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    const cardUUID = ref<string>(history.state.cardUUID);
    const cardProfile = ref<CardProfile>();

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

    async function createAccount(activationCode?: string) {
        try {
            const append = activationCode ? `?qrcode=${activationCode}` : "";
            await userStore.axiosInstance.post(`/cards/${cardUUID.value}/accounts` + append);
        } catch (error: any) {
            notificationStore.error("激活失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function updateAccount() {
        try {
            const resp = await userStore.axiosInstance.patch(`/cards/${cardUUID.value}/accounts`);
            const result: Partial<CardScoreUpdateResult> = resp.data;
            if (result && result.player_rating_old != result.player_rating_new) {
                notificationStore.success("更新成功", `DX Rating已更新: ${result.player_rating_old} -> ${result.player_rating_new}`);
                await refreshCard();
            }
        } catch (error: any) {
            notificationStore.error("更新失败", error.response.data.detail || "未知错误");
            throw error;
        }
    }

    async function patchPreferences(uuid?: string, preference?: Preference) {
        try {
            uuid = uuid ?? cardUUID.value!;
            preference = preference ?? cardProfile.value?.preferences;
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

    return { refreshCard, createAccount, updateAccount, createCard, patchPreferences, cardUUID, cardProfile }
})
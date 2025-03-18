import { defineStore } from "pinia"
import { useUserStore } from "./user";
import { useNotificationStore } from "./notification";
import type { Card, PreferencePublic } from "@/types";

export const useDraftStore = defineStore('draft', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();

    async function fetchDrafts(phone: string): Promise<Card[]> {
        try {
            const response = await userStore.axiosInstance.get(`/drafts?phone=${phone}`)
            return response.data
        } catch (error) {
            notificationStore.error("获取订单失败", `无法获取草稿列表，请联系开发者\n手机号码: ${phone}`);
            throw error
        }
    }

    async function createDraft(phone: string): Promise<Card> {
        try {
            const response = await userStore.axiosInstance.post(`/drafts?phone=${phone}`)
            return response.data
        } catch (error: any) {
            notificationStore.error("创建失败", error.response.data.detail);
            throw error
        }
    }

    async function fetchPreferences(uuid?: string): Promise<PreferencePublic> {
        try {
            const path = uuid ? `/drafts/${uuid}/preference` : '/defaults'
            const response = await userStore.axiosInstance.get(path)
            return response.data
        } catch (error) {
            notificationStore.error("获取配置失败", `无法获取草稿配置，请联系开发者\n卡片UUID: ${uuid || '未知'}`);
            throw error
        }
    }

    async function patchPreferences(uuid: string, preferences: PreferencePublic) {
        try {
            const response = await userStore.axiosInstance.patch(`/drafts/${uuid}/preference`, preferences)
            return response.status === 200
        } catch (error: any) {
            notificationStore.error("保存失败", error.response.data.detail);
            return false
        }
    }

    async function deleteDraft(uuid: string) {
        try {
            const response = await userStore.axiosInstance.delete(`/drafts/${uuid}`)
            return response.status === 200
        } catch (error: any) {
            notificationStore.error("删除失败", error.response.data.detail);
            return false
        }
    }

    return { fetchDrafts, createDraft, fetchPreferences, patchPreferences, deleteDraft }
})
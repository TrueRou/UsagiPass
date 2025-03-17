import { defineStore } from "pinia"
import { useUserStore } from "./user";
import type { Card, PreferencePublic } from "@/types";

export const useDraftStore = defineStore('draft', () => {
    const userStore = useUserStore();

    async function fetchDrafts(phone: string): Promise<Card[]> {
        try {
            const response = await userStore.axiosInstance.get(`/drafts?phone=${phone}`)
            return response.data
        } catch (error) {
            alert("无法获取草稿列表，请联系开发者\n调试ID: " + phone)
            throw error
        }
    }

    async function createDraft(phone: string): Promise<Card> {
        try {
            const response = await userStore.axiosInstance.post(`/drafts?phone=${phone}`)
            return response.data
        } catch (error: any) {
            alert(error.response.data.detail)
            throw error
        }
    }

    async function fetchPreferences(uuid?: string): Promise<PreferencePublic> {
        try {
            const path = uuid ? `/drafts/${uuid}/preference` : '/defaults'
            const response = await userStore.axiosInstance.get(path)
            return response.data
        } catch (error) {
            alert("无法获取草稿配置，请联系开发者\n调试ID: " + uuid)
            throw error
        }
    }

    async function patchPreferences(uuid: string, preferences: PreferencePublic) {
        try {
            const response = await userStore.axiosInstance.patch(`/drafts/${uuid}/preference`, preferences)
            return response.status === 200
        } catch (error: any) {
            alert(error.response.data.detail)
            return false
        }
    }

    return { fetchDrafts, createDraft, fetchPreferences, patchPreferences }
})
import { defineStore } from "pinia"
import { useUserStore } from "./user";

export const useCardStore = defineStore('card', () => {
    const userStore = useUserStore();

    async function fetchCard(uuid: string): Promise<CardProfile> {
        try {
            const response = await userStore.axiosInstance.get(`/cards/${uuid}/profile`)
            return response.data
        } catch (error) {
            alert("无法获取卡片信息，请联系开发者\n调试ID: " + uuid)
            throw error
        }
    }

    return { fetchCard }
})
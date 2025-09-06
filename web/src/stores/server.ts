import axios from "axios";
import { defineStore } from "pinia"
import { ref } from "vue";
import { useNotificationStore } from "./notification";

export const useServerStore = defineStore('server', () => {
    const serverNames: Record<number, string> = { 1: "水鱼", 2: "落雪", 3: "微信" }
    const serverKinds = ref<Record<string, Record<string, number[][]>> | null>(null)
    const notificationStore = useNotificationStore();

    const axiosInstance = ref(axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 10000,
    }));

    async function refreshKind() {
        try {
            const response = (await axiosInstance.value.get('/bits/standard'))
            serverKinds.value = response.data
        } catch (error) {
            notificationStore.error("服务器错误", "无法刷新图片类型信息，请联系开发者");
            console.error(error)
        }
    }

    return { axiosInstance, serverKinds, serverNames, refreshKind }
})
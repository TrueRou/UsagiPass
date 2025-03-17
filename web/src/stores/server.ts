import type { ServerMessage } from "@/types";
import axios from "axios";
import { defineStore } from "pinia"
import { ref } from "vue";

export const useServerStore = defineStore('server', () => {
    const serverNames: Record<number, string> = { 1: "水鱼", 2: "落雪", 3: "微信" }
    const serverMessage = ref<ServerMessage | null>(null)
    const serverKinds = ref<Record<string, Record<string, number[][]>> | null>(null)

    const axiosInstance = ref(axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 3000,
    }));

    async function refreshMotd() {
        try {
            const response = (await axiosInstance.value.get('/motd'))
            serverMessage.value = response.data
        } catch (error) {
            alert("无法获取服务器信息，可能是服务器正在维护")
            console.error(error)
        }
    }

    async function refreshKind() {
        try {
            const response = (await axiosInstance.value.get('/kinds'))
            serverKinds.value = response.data
        } catch (error) {
            alert("无法刷新图片类型信息，请联系开发者")
            console.error(error)
        }
    }

    return { axiosInstance, serverMessage, serverKinds, serverNames, refreshMotd, refreshKind }
})
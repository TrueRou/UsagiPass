import axios from "axios";
import { defineStore } from "pinia"
import { ref } from "vue";

export const useServerStore = defineStore('server', () => {
    const serverMessage = ref<ServerMessage | null>(null)

    const axiosInstance = ref(axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 3000,
    }));

    async function refreshMotd() {
        const response = (await axiosInstance.value.get('/motd'))
        if (response.status === 200) {
            serverMessage.value = response.data
        }
    }

    return { axiosInstance, serverMessage, refreshMotd }
})
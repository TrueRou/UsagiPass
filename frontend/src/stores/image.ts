import { defineStore } from "pinia"
import { ref } from "vue";
import { useUserStore } from "./user";

export const useImageStore = defineStore('image', () => {
    const userStore = useUserStore();
    const images = ref<Record<string, ImageDetail[]>>()

    async function refreshImages() {
        const response = await userStore.axiosInstance.get('/bits/')
        images.value = response.data.reduce((acc: Record<string, ImageDetail[]>, item: ImageDetail) => {
            if (!acc[item.kind]) {
                acc[item.kind] = [];
            }
            acc[item.kind].push(item);
            return acc;
        }, {});
    }

    return { images, refreshImages }
})
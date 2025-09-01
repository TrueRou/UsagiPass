import { defineStore } from "pinia"
import { ref } from "vue";
import { useUserStore } from "./user";
import { useNotificationStore } from "@/stores/notification";
import router from "@/router";
import type { Image, Kind, Preference } from "@/types";

export const useImageStore = defineStore('image', () => {
    const userStore = useUserStore();
    const notificationStore = useNotificationStore();
    const images = ref<Record<string, Image[]>>()
    const wanderingPreferences = ref<Preference>()

    async function refreshImages() {
        try {
            const response = await userStore.axiosInstance.get('/bits')
            images.value = response.data.reduce((acc: Record<string, Image[]>, item: Image) => {
                if (!acc[item.kind]) {
                    acc[item.kind] = [];
                }
                acc[item.kind].push(item);
                return acc;
            }, {});
        } catch (error: any) {
            notificationStore.error("获取失败", error.response.data.detail);
        }
    }

    async function uploadImage(name: string, kind: Kind, file: Blob) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            await userStore.axiosInstance.post(`/bits?name=${name}&kind=${kind}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            await refreshImages();
            router.back();
        } catch (error: any) {
            notificationStore.error("上传失败", error.response.data.detail);
        }
    }

    async function deleteImage(image: Image) {
        try {
            if (confirm(`确定删除 ${image.name} 吗？`)) {
                await userStore.axiosInstance.delete("/images/" + image.id)
                await refreshImages();
            }
        } catch (error: any) {
            notificationStore.error("删除失败", error.response.data.detail);
        }
    }

    async function patchImage(image: Image) {
        try {
            await userStore.axiosInstance.patch("/images/" + image.id + "?name=" + image.name);
            await refreshImages();
        } catch (error: any) {
            notificationStore.error("更新失败", error.response.data.detail);
        }
    }

    return { images, wanderingPreferences, refreshImages, uploadImage, deleteImage, patchImage }
})
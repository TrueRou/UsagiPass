import { defineStore } from "pinia"
import { ref } from "vue";
import { useUserStore } from "./user";
import router from "@/router";
import type { ImageDetail, ImagePublic, Kind, PreferencePublic } from "@/types";

export const useImageStore = defineStore('image', () => {
    const userStore = useUserStore();
    const images = ref<Record<string, ImageDetail[]>>()
    const wanderingPreferences = ref<PreferencePublic>()

    async function refreshImages() {
        try {
            const response = await userStore.axiosInstance.get('/bits')
            images.value = response.data.reduce((acc: Record<string, ImageDetail[]>, item: ImageDetail) => {
                if (!acc[item.kind]) {
                    acc[item.kind] = [];
                }
                acc[item.kind].push(item);
                return acc;
            }, {});
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    async function uploadImage(name: string, kind: Kind, file: Blob) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            await userStore.axiosInstance.post(`/images?name=${name}&kind=${kind}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            await refreshImages();
            router.back();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    async function deleteImage(image: ImagePublic) {
        try {
            if (confirm(`确定删除 ${image.name} 吗？`)) {
                await userStore.axiosInstance.delete("/images/" + image.id)
                await refreshImages();
            }
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    async function patchImage(image: ImagePublic) {
        try {
            await userStore.axiosInstance.patch("/images/" + image.id + "?name=" + image.name);
            await refreshImages();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    return { images, wanderingPreferences, refreshImages, uploadImage, deleteImage, patchImage }
})
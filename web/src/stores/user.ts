import router from "@/router"
import axios from "axios"
import { defineStore } from "pinia"
import { computed, ref, type Ref } from "vue"
import { type Router } from "vue-router"
import { useImageStore } from "./image"

export const useUserStore = defineStore('user', () => {
    const imageStore = useImageStore();

    const token = ref(localStorage.getItem('token'));
    const maimaiCode = ref("");
    const timeLimit = ref("12:00:00");
    const simplifiedCode = computed(() => maimaiCode.value.slice(8, 28).match(/.{1,4}/g)?.join(' '));
    const axiosInstance = computed(() => axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 10000,
        headers: { 'Authorization': `Bearer ${token.value}` },
    }));
    const isSignedIn = ref(false);
    const userProfile = ref<UserProfile | null>(null);
    const cropperImage = ref<string | null>(null);

    async function login(target: string, username: string, password: string) {
        try {
            const data = await axiosInstance.value.post(`/accounts/token/${target}`, new URLSearchParams({
                username,
                password
            }));
            localStorage.setItem('token', data.data.access_token);
            token.value = data.data.access_token;
            await refreshUser();
            // refresh images after login, fetch user uploaded images
            if (imageStore.images) await imageStore.refreshImages();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    function logout() {
        localStorage.removeItem('token');
        token.value = null;
        isSignedIn.value = false;
        userProfile.value = null;
    }

    async function bind(target: string, username: string, password: string) {
        try {
            await axiosInstance.value.post(`/accounts/bind/${target}`, new URLSearchParams({ username, password }));
            await refreshUser();
            router.back();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    async function refreshUser() {
        try {
            const response = (await axiosInstance.value.get('/users/profile'));
            userProfile.value = response.data;
            isSignedIn.value = true;
        } catch (error) {
            isSignedIn.value = false;
            userProfile.value = null;
        }
    }

    async function patchPreferences() {
        try {
            await axiosInstance.value.patch('/users/preference', userProfile.value!.preferences);
            await refreshUser();
            router.back();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    async function patchPreferServer(prefer_server: number) {
        try {
            await axiosInstance.value.patch('/users', { prefer_server: prefer_server });
            await refreshUser();
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    const updateProber = async () => {
        if (navigator.userAgent.toLowerCase().indexOf('micromessenger') == -1) {
            alert("无法获取玩家信息, 请在微信环境中更新查分器");
            return false;
        }
        try {
            const testWahlap = await axios.get("http://tgk-wcaime.wahlap.com/test");
            // 502 is wahlap's original status code for proxy with old rules
            if (testWahlap.status == 502) {
                alert("当前代理配置已过时, 请更新订阅后重试");
                return false;
            }
        } catch (error: any) { } // bypass cors
        try {
            const resp = await axiosInstance.value.post("/accounts/update/oauth");
            window.location.href = resp.data.url;
        } catch (error: any) {
            alert(error.response.data.detail);
        }
    }

    const changeImagePicker = (imagePicker: HTMLInputElement, uploadKind: string, cropperImage: Ref<string | null, string | null>, router: Router) => {
        const file = imagePicker.files?.[0];
        if (file && uploadKind) {
            const reader = new FileReader();
            reader.onload = function (ev) {
                cropperImage.value = ev.target?.result as string;
                router.push({ name: 'cropper', params: { kind: uploadKind } });
            }
            reader.readAsDataURL(file);
        }
    }

    const openImagePicker = (kind: string, picker: HTMLInputElement) => {
        if (!picker) return;
        picker.removeEventListener('change', () => { changeImagePicker(picker, kind, cropperImage, router) });
        picker.addEventListener('change', () => { changeImagePicker(picker, kind, cropperImage, router) });
        picker.click();
    }

    return {
        axiosInstance,
        maimaiCode,
        timeLimit,
        simplifiedCode,
        userProfile,
        isSignedIn,
        cropperImage,
        refreshUser,
        patchPreferences,
        patchPreferServer,
        updateProber,
        openImagePicker,
        login,
        logout,
        bind,
    }
})
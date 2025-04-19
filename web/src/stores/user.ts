import router from "@/router"
import axios from "axios"
import { defineStore } from "pinia"
import { computed, ref, type Ref } from "vue"
import { type Router } from "vue-router"
import { useImageStore } from "./image"
import { useNotificationStore } from "./notification"
import { AccountServer, type Kind, type UserProfile } from "@/types"

export const useUserStore = defineStore('user', () => {
    const imageStore = useImageStore();
    const notificationStore = useNotificationStore();

    const token = ref(localStorage.getItem('token'));
    const maimaiCode = ref("");
    const timeLimit = ref("12:00:00");
    const isSignedIn = ref(false);
    const userProfile = ref<UserProfile | null>(null);
    const cropperImage = ref<string | null>(null);

    const simplifiedCode = computed(() => maimaiCode.value.slice(8, 28).match(/.{1,4}/g)?.join(' '));
    const axiosInstance = computed(() => axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 10000,
        headers: { 'Authorization': `Bearer ${token.value}` },
    }));
    const preferAccount = computed(() => userProfile.value?.accounts[userProfile.value.prefer_server]);

    async function login(target: string, username: string, password: string) {
        try {
            const data = await axiosInstance.value.post(`/accounts/token/${target}`, new URLSearchParams({
                username,
                password
            }));
            localStorage.setItem('token', data.data.access_token);
            token.value = data.data.access_token;
            await refreshUser();
            // 如果之前获取过图片列表，刷新列表
            if (imageStore.images) await imageStore.refreshImages();
            notificationStore.success("登录成功", `欢迎回来，${preferAccount.value?.nickname}`);
            return true;
        } catch (error: any) {
            notificationStore.error("登录失败", error.response?.data?.detail || "未知错误");
            return false;
        }
    }

    function logout(refresh = true) {
        localStorage.removeItem('token');
        token.value = null;
        isSignedIn.value = false;
        userProfile.value = null;
        if (refresh) router.go(0);
    }

    async function bind(server: AccountServer, username: string, password: string) {
        try {
            await axiosInstance.value.post(`/accounts/bind/${AccountServer[server].toLowerCase()}`, new URLSearchParams({ username, password }));
            await refreshUser();
            notificationStore.success("绑定成功", `查分器账户绑定成功`);
            router.back();
        } catch (error: any) {
            notificationStore.error("绑定失败", error.response?.data?.detail || "未知错误");
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
            notificationStore.success("保存成功", "个人偏好设置已保存");
            router.back();
        } catch (error: any) {
            notificationStore.error("保存失败", error.response?.data?.detail || "未知错误");
        }
    }

    async function patchPreferServer(prefer_server: number) {
        try {
            await axiosInstance.value.patch('/users', { prefer_server: prefer_server });
            await refreshUser();
            notificationStore.success("设置成功", `已将${prefer_server === 1 ? '水鱼' : '落雪'}设为优先数据源`);
        } catch (error: any) {
            notificationStore.error("设置失败", error.response?.data?.detail || "未知错误");
        }
    }

    const updateProber = async () => {
        if (navigator.userAgent.toLowerCase().indexOf('micromessenger') == -1) {
            notificationStore.error("更新失败", "无法获取玩家信息，请在微信环境中更新查分器");
            return;
        }
        try {
            const testWahlap = await axios.get("http://tgk-wcaime.wahlap.com/test");
            // 502是历史遗留规则中的一个错误码，代表代理配置过时
            if (testWahlap.status == 502) {
                notificationStore.warning("代理配置过时", "当前代理配置已过时，请更新订阅后重试");
                return;
            }
        } catch (error: any) { }
        try {
            const resp = await axiosInstance.value.post("/accounts/update/oauth");
            window.location.href = resp.data.url;
        } catch (error: any) {
            notificationStore.error("更新失败", error.response?.data?.detail || "未知错误");
        }
    }

    const changeImagePicker = (imagePicker: HTMLInputElement, kind: Kind, cropperImage: Ref<string | null, string | null>, router: Router) => {
        const file = imagePicker.files?.[0];
        if (file && kind) {
            const reader = new FileReader();
            reader.onload = function (ev) {
                cropperImage.value = ev.target?.result as string;
                router.push({ name: 'cropper', params: { kind: kind } });
            }
            reader.readAsDataURL(file);
        }
    }

    const openImagePicker = (kind: Kind, imagePicker: HTMLInputElement) => {
        if (imagePicker) {
            imagePicker.onchange = () => changeImagePicker(imagePicker, kind, cropperImage, router);
            imagePicker.click();
        }
    }

    return {
        axiosInstance,
        token,
        isSignedIn,
        userProfile,
        cropperImage,
        maimaiCode,
        timeLimit,
        simplifiedCode,
        preferAccount,
        login,
        logout,
        bind,
        refreshUser,
        patchPreferences,
        patchPreferServer,
        updateProber,
        openImagePicker
    }
})
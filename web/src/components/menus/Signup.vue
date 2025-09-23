<script setup lang="ts">
import { ref, computed } from 'vue';
import { useUserStore } from '@/stores/user';
import TermsLink from '@/components/widgets/TermsLink.vue';
import router from '@/router';

const userStore = useUserStore();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const loginTarget = ref('');
const termsAccepted = ref(false);
const termsLinkRef = ref<InstanceType<typeof TermsLink>>();

// 计算按钮是否可用
const isButtonEnabled = computed(() => termsAccepted.value && !isLoading.value);

// 计算按钮样式类
const wechatButtonClass = computed(() => 
    isButtonEnabled.value 
        ? 'bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-600 mt-2 mb-2 w-[250px] flex items-center justify-center gap-2 transition-opacity'
        : 'bg-green-500 text-white font-bold py-2 px-4 rounded mt-2 mb-2 w-[250px] flex items-center justify-center gap-2 opacity-50 transition-opacity'
);

const loginButtonClass = computed(() => 
    isButtonEnabled.value 
        ? 'bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 mb-2 w-[250px] flex items-center justify-center gap-2 transition-opacity'
        : 'bg-blue-500 text-white font-bold py-2 px-4 rounded mt-2 mb-2 w-[250px] flex items-center justify-center gap-2 opacity-50 transition-opacity'
);

const handleWechatLogin = () => {
    if (!termsAccepted.value) {
        termsLinkRef.value?.shake();
        // 调用 store 方法，让它显示统一的协议提示
        userStore.updateProber();
        return;
    }
    
    if (!isButtonEnabled.value) return;
    userStore.updateProber();
};

const handleLoginRedirect = () => {
    if (!termsAccepted.value) {
        termsLinkRef.value?.shake();
        // 调用 login 方法仅触发协议检查，参数留空不会实际登录
        userStore.login('', '', '');
        return;
    }
    
    if (!isButtonEnabled.value) return;
    router.push({ name: 'login' });
};

const handleLogin = async (target: string) => {
    if (isLoading.value) return;

    isLoading.value = true;
    loginTarget.value = target;

    try {
        const result = await userStore.login(target, username.value, password.value);
        if (result) {
            if (history.state.useBack) router.back();
            else router.replace({ name: 'home' });
        }
    } catch (error) {
        console.error('Login failed:', error);
    } finally {
        isLoading.value = false;
    }
};
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <h1 class="mt-2 text-xl font-bold">登录 UsagiPass</h1>
        <h2 class="mt-1 mb-3 text-xs text-gray-600 text-center">使用微信或查分器账号登录<br>未登录过 UsagiPass 的微信 / 查分器账号在登录后将自动创建账户
        </h2>
        <button 
            :class="wechatButtonClass"
            @click="handleWechatLogin">
            <img class="h-[24px] w-[24px]" src="../../assets/misc/wechat.svg">
            使用微信登录
        </button>
        <button 
            :class="loginButtonClass"
            @click="handleLoginRedirect">
            <img class="h-[20px] w-[20px]" src="../../assets/misc/maimai.png">
            使用查分器账号登录
        </button>
        <TermsLink v-model="termsAccepted" ref="termsLinkRef" />
    </div>
</template>
<style scoped>
input {
    outline-style: none;
    border: 2px solid #000;
    border-radius: 5px;
    width: 200px;
    height: 100%;
    padding: 0;
    padding: 10px 10px;
    box-sizing: border-box;

    &:focus {
        border-color: #60a5fa;
        outline: 0;
        -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
        box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
    }
}


select {
    background: #fafdfe;
    width: 200px;
    height: 100%;
    padding: 10px 10px;
    box-sizing: border-box;
    border: 2px solid #000;
    border-radius: 5px;
}
</style>
<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import TermsLink from '@/components/widgets/TermsLink.vue';
import router from '@/router';

const userStore = useUserStore();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const loginTarget = ref('');

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
        <h1 class="mt-2 text-xl font-bold">登录UsagiPass</h1>
        <h2 class="mt-1 mb-3 text-xs text-gray-600">使用水鱼或落雪账户登录<br>落雪登录使用<b> 个人 API 密钥 </b>作为密码
        </h2>
        <input type="text" v-model="username" placeholder="用户名" :disabled="isLoading" />
        <input class="mt-2" type="password" v-model="password" placeholder="密码 / 个人 API 密钥" :disabled="isLoading" />
        <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 w-[200px]"
            @click="handleLogin('divingfish')" :disabled="isLoading">
            <span v-if="isLoading && loginTarget === 'divingfish'" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                </svg>
                登录中...
            </span>
            <span v-else>使用水鱼登录</span>
        </button>
        <button class="bg-pink-500 text-white font-bold py-2 px-4 rounded hover:bg-pink-600 mt-2 mb-2 w-[200px]"
            @click="handleLogin('lxns')" :disabled="isLoading">
            <span v-if="isLoading && loginTarget === 'lxns'" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                </svg>
                登录中...
            </span>
            <span v-else>使用落雪登录</span>
        </button>
        <TermsLink />
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
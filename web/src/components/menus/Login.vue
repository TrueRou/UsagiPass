<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import TermsLink from '@/components/widgets/TermsLink.vue';

const userStore = useUserStore();

const username = ref('');
const password = ref('');

const login = async (target: string) => await userStore.login(target, username.value, password.value);
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <h1 class="mt-2 text-xl font-bold">登录UsagiPass</h1>
        <h2 class="mt-1 mb-3 text-xs text-gray-600">使用水鱼或落雪账户登录<br>落雪登录使用<b> 个人 API 密钥 </b>作为密码
        </h2>
        <input type="text" v-model="username" placeholder="用户名" />
        <input class="mt-2" type="password" v-model="password" placeholder="密码 / 个人 API 密钥" />
        <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 w-[200px]"
            @click="login('divingfish')">使用水鱼登录</button>
        <button class="bg-pink-500 text-white font-bold py-2 px-4 rounded hover:bg-pink-600 mt-2 mb-2 w-[200px]"
            @click="login('lxns')">使用落雪登录</button>
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
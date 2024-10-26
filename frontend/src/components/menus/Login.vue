<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');

const userStore = useUserStore();
const router = useRouter();

const login = async () => {
    const result = await userStore.login(username.value, password.value);
    if (result) router.push({ name: 'home' });
};
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <h1 class="mt-2 text-xl font-bold">登录UsagiPass</h1>
        <h2 class="mt-1 mb-3 text-xs text-gray-600">请使用水鱼查分器账户登录<br>我们不会明文保存您的密码</h2>
        <input type="text" v-model="username" placeholder="用户名" />
        <input class="mt-2" type="password" v-model="password" placeholder="密码" />
        <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 mb-2 w-[200px]"
            @click="login">登录</button>
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
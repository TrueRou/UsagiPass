<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import TermsLink from '@/components/widgets/TermsLink.vue';
import { AccountServer } from '@/types';

const props = defineProps<{
    server: AccountServer;
}>()

type Entries = 'title' | 'username' | 'password' | 'subtitle' | 'subtitle2';

const serverLang: Record<AccountServer, Record<Entries, string>> = {
    [AccountServer.DIVINGFISH]: {
        title: '绑定水鱼账户',
        username: '用户名',
        password: '密码',
        subtitle: '请使用水鱼用户名与密码进行鉴权并绑定',
        subtitle2: '若水鱼账户已经绑定过其他账号, 请联系开发者'
    },
    [AccountServer.LXNS]: {
        title: '绑定落雪账户',
        username: '用户名',
        password: '个人 API 密钥',
        subtitle: '请使用落雪用户名与个人 API 密钥进行鉴权并绑定',
        subtitle2: '若落雪账户已经绑定过其他账号, 请联系开发者'
    },
    [AccountServer.WECHAT]: {
        title: '绑定微信账户',
        username: '微信 ID',
        password: '微信 Token',
        subtitle: '暂时不支持直接绑定微信账号',
        subtitle2: '如果您对绑定微信账号有疑问，请联系开发者'
    }
}

const username = ref('');
const password = ref('');

const userStore = useUserStore();
const router = useRouter();

const bind = async () => await userStore.bind(props.server, username.value, password.value);
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <h1 class="mt-2 text-xl font-bold">{{ serverLang[props.server].title }}</h1>
        <h2 class="mt-1 text-xs text-gray-600">{{ serverLang[props.server].subtitle }}</h2>
        <h2 class="mt-1 mb-3 text-xs text-gray-600">{{ serverLang[props.server].subtitle2 }}</h2>
        <input type="text" v-model="username" :placeholder="serverLang[props.server].username" />
        <input class="mt-2" type="password" v-model="password" :placeholder="serverLang[props.server].password" />
        <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 w-[200px]"
            @click="bind">绑定</button>
        <button class="bg-gray-500 text-white font-bold py-2 px-4 rounded hover:bg-gray-600 mt-2 w-[200px]"
            @click="router.back()">取消</button>
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
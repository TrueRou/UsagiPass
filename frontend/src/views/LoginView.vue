<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const form = ref({
  username: '',
  password: '',
});

const userStore = useUserStore();
const router = useRouter();

const login = async () => {
  const result = await userStore.login(form.value.username, form.value.password);
  if (result) router.push('/');
};
</script>
<template>
  <div class="bg-blue-400 flex flex-col items-center h-full w-full">
    <div class="flex flex-col items-center h-full w-full sm:w-[640px] pl-4 pr-4 pt-2 pb-2">
      <div class="flex flex-col items-center h-full w-full rounded bg-white p-4 overflow-y-scroll">
        <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
          <h1 class="mt-2 text-xl font-bold">登录UsagiPass</h1>
          <h2 class="mt-1 mb-3 text-xs text-gray-600">请使用水鱼查分器账户登录<br>我们不会明文保存您的密码</h2>
          <input type="text" v-model="form.username" placeholder="用户名" />
          <input class="mt-2" type="password" v-model="form.password" placeholder="密码" />
          <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mt-2 mb-2 w-[200px]"
            @click="login">登录</button>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
::-webkit-scrollbar {
  display: none;
}

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
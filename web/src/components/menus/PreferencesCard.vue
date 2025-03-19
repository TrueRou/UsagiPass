<script setup lang="tsx">
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();

</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">开发者</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex items-center">
                <a href="https://github.com/TrueRou"><img class="w-12 h-12 rounded-full ml-2"
                        src="../../assets/misc/avatar.webp"></a>

                <div class="flex flex-col p-2">
                    <span><a href="https://github.com/TrueRou">兔肉</a></span>
                    <span class="text-gray-600" style="font-size: 12px;">本项目已在Github开源</span>
                </div>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold py-2 px-2 h-[40px] w-[40px] rounded hover:bg-blue-600 cursor-pointer"
                    href="https://github.com/TrueRou/UsagiPass">
                    <img src="../../assets/misc/github-mark-white.svg">
                </a>
                <a class="ml-2 bg-blue-500 text-white font-bold py-1 px-1 h-[40px] w-[40px] rounded hover:bg-blue-600 text-sm cursor-pointer"
                    href="https://afdian.com/a/turou">
                    <img src="../../assets/misc/afdian.svg">
                </a>
            </div>
        </div>
    </div>
    <div class="flex justify-end w-full mt-2 mr-5">
        <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600"
            v-on:click="userStore.patchPreferences()">
            保存
        </button>
    </div>
</template>
<style scoped>
input {
    outline-style: none;
    border: 2px solid #000;
    border-radius: 5px;
    width: 200px;

    @media (max-width: 600px) {
        width: 160px;
    }

    @media (max-width: 380px) {
        width: 140px;
    }

    height: 44.5px;
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

    @media (max-width: 600px) {
        width: 160px;
    }

    @media (max-width: 380px) {
        width: 140px;
    }

    height: 44.5px;
    padding: 10px 10px;
    box-sizing: border-box;
    border: 2px solid #000;
    border-radius: 5px;
}
</style>
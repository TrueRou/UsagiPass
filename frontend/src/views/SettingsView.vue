<script lang="ts" setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const settings = ref<UserPreferencePublic>(userStore.userProfile!.preferences);
</script>
<template>
    <div class="bg-blue-400 flex flex-col items-center h-full w-full">
        <div class="flex flex-col items-center h-full w-full sm:w-[640px] pl-4 pr-4 pt-2 pb-2">
            <div class="flex flex-col items-center h-full w-full rounded bg-white p-4">
                <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">卡面设置</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>好友号码</span>
                            <span class="text-gray-600" style="font-size: 10px;">填写12位或15位的好友号码</span>
                        </div>
                        <div><input v-model="settings.friend_code"></div>
                    </div>
                </div>
                <div
                    class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">覆盖设置</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>玩家昵称</span>
                            <span class="text-gray-600" style="font-size: 10px;">覆盖Diving-Fish返回的玩家昵称</span>
                        </div>
                        <div><input v-model="settings.display_name"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>DX分数</span>
                            <span class="text-gray-600" style="font-size: 10px;">覆盖Diving-Fish返回的DX分数</span>
                        </div>
                        <div><input v-model="settings.dx_rating"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>人物名称</span>
                            <span class="text-gray-600" style="font-size: 10px;">覆盖卡面左下方的人物名称</span>
                        </div>
                        <div><input v-model="settings.character_name"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>卡片号码</span>
                            <span class="text-gray-600" style="font-size: 10px;">覆盖卡面下方的20位卡片号码</span>
                        </div>
                        <div><input v-model="settings.simplified_code"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>游戏版本</span>
                            <span class="text-gray-600" style="font-size: 10px;">覆盖卡面下方的maimai版本</span>
                        </div>
                        <div><input v-model="settings.maimai_version"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
input {
    outline-style: none;
    border: 2px solid #000;
    border-radius: 5px;
    width: 100%;
    height: 100%;
    padding: 0;
    padding: 10px 15px;
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
</style>
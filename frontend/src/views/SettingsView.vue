<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const settings = ref<UserPreferencePublic>(userStore.userProfile!.preferences);
const profile = ref<UserProfile>(userStore.userProfile!);
const images = ref<Record<string, ImagePublic[]>>()

const r = (resource_id: string) => import.meta.env.VITE_URL + "/images/" + resource_id;

const submit = async () => {
    if (await userStore.patchPreferences(settings.value)) {
        router.push('/');
    }
}

const refreshRating = async () => {
    await userStore.updateRating();
    await userStore.refreshUser();
    profile.value = userStore.userProfile!;
    alert("DXRating已刷新");
}

onMounted(async () => {
    images.value = await userStore.getImages();
});
</script>
<template>
    <div class="bg-blue-400 flex flex-col items-center h-full w-full">
        <div class="flex flex-col items-center h-full w-full sm:w-[640px] pl-4 pr-4 pt-2 pb-2">
            <div class="flex flex-col items-center h-full w-full rounded bg-white p-4 overflow-y-scroll">
                <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">开发者</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex items-center">
                            <a href="https://github.com/TrueRou"><img class="w-12 h-12 rounded-full ml-2"
                                    src="../assets/misc/avatar.webp"></a>

                            <div class="flex flex-col p-2">
                                <span><a href="https://github.com/TrueRou">兔肉</a></span>
                                <span class="text-gray-600" style="font-size: 12px;">本项目已在Github开源</span>
                            </div>
                        </div>
                        <div class="flex items-center">
                            <a class="bg-blue-500 text-white font-bold py-2 px-2 h-[40px] w-[40px] rounded hover:bg-blue-600 cursor-pointer"
                                href="https://github.com/TrueRou/UsagiPass">
                                <img src="../assets/misc/github-mark-white.svg">
                            </a>
                            <a class="ml-2 bg-blue-500 text-white font-bold py-1 px-1 h-[40px] w-[40px] rounded hover:bg-blue-600 text-sm cursor-pointer"
                                href="https://afdian.com/a/turou">
                                <img src="../assets/misc/afdian.svg">
                            </a>
                        </div>
                    </div>
                </div>
                <div
                    class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">账户设置</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>{{ profile.nickname }} ({{ profile.username }})</span>
                            <span class="text-gray-600" style="font-size: 12px;">DXRating: {{ profile.player_rating
                                }}</span>
                        </div>
                        <div class="flex items-center">
                            <a class="bg-blue-500 text-white font-bold py-2 px-2 h-[40px] w-[40px] rounded hover:bg-blue-600 cursor-pointer"
                                @click="refreshRating">
                                <img src="../assets/misc/refresh.svg">
                            </a>
                            <a class="ml-2 bg-blue-500 text-white font-bold py-1 px-1 h-[40px] w-[40px] rounded hover:bg-blue-600 text-sm cursor-pointer"
                                @click="userStore.logout">
                                <img class="pl-1.5 pt-1" src="../assets/misc/logout.svg">
                            </a>
                        </div>
                    </div>
                </div>
                <div
                    class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">卡面设置</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>好友号码</span>
                            <span class="text-gray-600" style="font-size: 12px;">填写12位或15位的好友号码</span>
                        </div>
                        <div><input v-model="settings.friend_code"></div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>二维码尺寸</span>
                            <span class="text-gray-600" style="font-size: 12px;">如果机台无法识别, 请增大二维码尺寸</span>
                        </div>
                        <select v-model="settings.qr_size">
                            <option :value="12">小</option>
                            <option :value="15">中</option>
                            <option :value="20">大</option>
                            <option :value="24">标准</option>
                            <option :value="28">标准+</option>
                            <option :value="32">标准++</option>
                        </select>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>背景图片</span>
                            <span class="text-gray-600" style="font-size: 12px;">选择作为卡面背景的图片</span>
                        </div>
                        <div>
                            <select v-model="settings.background.id">
                                <option v-for="item in images?.background" :value="item.id">{{ item.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>边框图片</span>
                            <span class="text-gray-600" style="font-size: 12px;">选择作为卡面边框的图片</span>
                        </div>
                        <div>
                            <select v-model="settings.frame.id">
                                <option v-for="item in images?.frame" :value="item.id">{{ item.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>人物图片</span>
                            <span class="text-gray-600" style="font-size: 12px;">选择作为卡面人物的图片</span>
                        </div>
                        <div>
                            <select v-model="settings.character.id">
                                <option v-for="item in images?.character" :value="item.id">{{ item.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>PASS图片</span>
                            <span class="text-gray-600" style="font-size: 12px;">选择作为卡面PassName的图片</span>
                        </div>
                        <div>
                            <select v-model="settings.passname.id">
                                <option v-for="item in images?.passname" :value="item.id">{{ item.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex flex-col ml-2 mr-2">
                        <div class="flex justify-between items-center w-full mt-2">
                            <div class="flex flex-col flex-1 items-center justify-between"><img
                                    :src="r(settings.background.id)"></div>
                            <div class="flex flex-col flex-1 items-center justify-between"><img
                                    :src="r(settings.frame.id)"></div>
                            <div class="flex flex-col flex-1 items-center justify-between"><img
                                    :src="r(settings.character.id)"></div>
                            <div class="flex flex-col flex-1 items-center justify-between"><img
                                    :src="r(settings.passname.id)"></div>
                        </div>
                        <div class="flex justify-between items-center w-full mt-2">
                            <div class="flex flex-col flex-1 items-center justify-between">
                                <p class="text-gray-600" style="font-size: 12px;">背景预览</p>
                            </div>
                            <div class="flex flex-col flex-1 items-center justify-between">
                                <p class="text-gray-600" style="font-size: 12px;">边框预览</p>
                            </div>
                            <div class="flex flex-col flex-1 items-center justify-between">
                                <p class="text-gray-600" style="font-size: 12px;">人物预览</p>
                            </div>
                            <div class="flex flex-col flex-1 items-center justify-between">
                                <p class="text-gray-600" style="font-size: 12px;">PASS预览</p>
                            </div>
                        </div>
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
                            <span class="text-gray-600" style="font-size: 12px;">覆盖Diving-Fish返回的玩家昵称</span>
                        </div>
                        <div><input v-model="settings.display_name"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>DX分数</span>
                            <span class="text-gray-600" style="font-size: 12px;">覆盖Diving-Fish返回的DX分数</span>
                        </div>
                        <div><input v-model="settings.dx_rating"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>人物名称</span>
                            <span class="text-gray-600" style="font-size: 12px;">覆盖卡面左下方的人物名称</span>
                        </div>
                        <div><input v-model="settings.character_name"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>卡片号码</span>
                            <span class="text-gray-600" style="font-size: 12px;">覆盖卡面下方的20位卡片号码</span>
                        </div>
                        <div><input v-model="settings.simplified_code"></div>
                    </div>
                    <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
                    <div class="flex justify-between items-center w-full">
                        <div class="flex flex-col p-2">
                            <span>游戏版本</span>
                            <span class="text-gray-600" style="font-size: 12px;">覆盖卡面下方的maimai版本</span>
                        </div>
                        <div><input v-model="settings.maimai_version"></div>
                    </div>
                </div>
                <!-- class hidden -> flex -->
                <div
                    class="hidden flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
                    <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
                        <h1 class="font-bold text-white">自定义图片</h1>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>上传背景</span>
                            <span class="text-gray-600" style="font-size: 12px;">上传自定义背景图片 (768 * 1052)</span>
                        </div>
                        <div>
                            <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600">
                                上传
                            </button>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>上传边框</span>
                            <span class="text-gray-600" style="font-size: 12px;">上传自定义边框图片 (768 * 1052)</span>
                        </div>
                        <div>
                            <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600">
                                上传
                            </button>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>上传人物</span>
                            <span class="text-gray-600" style="font-size: 12px;">上传自定义人物图片 (768 * 1052)</span>
                        </div>
                        <div>
                            <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600">
                                上传
                            </button>
                        </div>
                    </div>
                    <div class="flex justify-between items-center w-full mt-2">
                        <div class="flex flex-col p-2">
                            <span>上传PASS</span>
                            <span class="text-gray-600" style="font-size: 12px;">上传自定义PASS图片 (338 * 112)</span>
                        </div>
                        <div>
                            <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600">
                                上传
                            </button>
                        </div>
                    </div>
                </div>
                <div class="flex justify-end w-full mt-2 mr-5">
                    <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600"
                        v-on:click="submit">
                        保存
                    </button>
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
    height: 44.5px;
    padding: 10px 10px;
    box-sizing: border-box;
    border: 2px solid #000;
    border-radius: 5px;
}
</style>
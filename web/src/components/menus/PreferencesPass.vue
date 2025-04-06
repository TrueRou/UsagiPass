<script setup lang="tsx">
import { useImageStore } from '@/stores/image';
import { useServerStore } from '@/stores/server';
import { useUserStore } from '@/stores/user';
import { AccountServer, type Kind } from '@/types';
import { ref, useTemplateRef } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();
const imageStore = useImageStore();
const serverStore = useServerStore();

const imagePicker = useTemplateRef('image-picker');
const userProfile = ref(userStore.userProfile);

const r = (resource_id: string) => import.meta.env.VITE_URL + "/images/" + resource_id;
const openPicker = (kind: Kind) => userStore.openImagePicker(kind, imagePicker.value!);

const openGallery = (kind: Kind) => {
    imageStore.wanderingPreferences = userProfile.value!.preferences;
    router.push({ name: 'gallery', params: { kind: kind } })
};

const bindBtn = (server: AccountServer) => {
    const isBinded = userStore.userProfile!.accounts[server];
    const colorSets = { orange: ["bg-orange-500", "hover:bg-orange-600"], blue: ["bg-blue-500", "hover:bg-blue-600"] };
    const classNames = ["text-white", "font-bold", "py-2", "px-4", "rounded", ...colorSets[isBinded ? 'orange' : 'blue']];
    return (
        <RouterLink class={classNames} to={{ name: "bind", params: { server } }}>
            {isBinded ? '改绑' : '绑定'}
        </RouterLink>
    );
};
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
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">账户设置</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>
                    {{ userStore.preferAccount!.nickname }} ({{ userStore.userProfile!.username }})
                </span>
                <span class="text-gray-600" style="font-size: 12px;">
                    优先使用 <b>{{ serverStore.serverNames[userStore.userProfile!.prefer_server] }}</b> 数据
                    DXRating: {{ userStore.preferAccount!.player_rating }}
                </span>
            </div>
            <div class="flex items-center">
                <button
                    class="bg-gradient-to-r from-pink-500 to-blue-500 text-white font-bold py-2 px-2 rounded hover:from-pink-600 hover:to-blue-600 text-nowrap"
                    @click="userStore.updateProber">
                    更新查分器
                </button>
                <a class="ml-2 bg-red-500 text-white font-bold py-1 px-1 h-[40px] w-[40px] rounded hover:bg-red-600 text-sm cursor-pointer"
                    @click="userStore.logout(true)">
                    <img class="pl-1.5 pt-1" src="../../assets/misc/logout.svg">
                </a>
            </div>
        </div>
    </div>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">卡面设置</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>好友号码</span>
                <span class="text-gray-600" style="font-size: 12px;">填写12位或15位的好友号码</span>
            </div>
            <div><input v-model="userProfile!.preferences.friend_code"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>二维码尺寸</span>
                <span class="text-gray-600" style="font-size: 12px;">如果机台无法识别, 请增大二维码尺寸</span>
            </div>
            <div>
                <select v-model="userProfile!.preferences.qr_size">
                    <option :value="-1">隐藏</option>
                    <option :value="12">小</option>
                    <option :value="15">中</option>
                    <option :value="20">大</option>
                    <option :value="24">标准</option>
                    <option :value="28">标准+</option>
                    <option :value="32">标准++</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>背景图片</span>
                <span class="text-gray-600" style="font-size: 12px;">选择卡面背景图片</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer mr-1"
                    @click="openGallery('background')">
                    <img src="../../assets/misc/images.svg">
                </a>
                <select v-model="userProfile!.preferences.background.id">
                    <option v-for="item in imageStore.images?.background" :value="item.id">{{ item.name }}</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>边框图片</span>
                <span class="text-gray-600" style="font-size: 12px;">选择卡面边框图片</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer mr-1"
                    @click="openGallery('frame')">
                    <img src="../../assets/misc/images.svg">
                </a>
                <select v-model="userProfile!.preferences.frame.id">
                    <option v-for="item in imageStore.images?.frame" :value="item.id">{{ item.name }}</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>人物图片</span>
                <span class="text-gray-600" style="font-size: 12px;">选择卡面人物图片</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer mr-1"
                    @click="openGallery('character')">
                    <img src="../../assets/misc/images.svg">
                </a>
                <select v-model="userProfile!.preferences.character.id">
                    <option v-for="item in imageStore.images?.character" :value="item.id">{{ item.name }}</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>通行证图片</span>
                <span class="text-gray-600" style="font-size: 12px;">选择卡面通行证图片</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer mr-1"
                    @click="openGallery('passname')">
                    <img src="../../assets/misc/images.svg">
                </a>
                <select v-model="userProfile!.preferences.passname.id">
                    <option v-for="item in imageStore.images?.passname" :value="item.id">{{ item.name }}</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>镭射设置</span>
                <span class="text-gray-600" style="font-size: 12px;">背景镭射层的显示样式</span>
            </div>
            <div>
                <select v-model="userProfile!.preferences.mask_type">
                    <option :value="0">未启用</option>
                    <option :value="1">动态渐变</option>
                </select>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex flex-col ml-2 mr-2">
            <div class="flex justify-between items-center w-full mt-2">
                <div class="flex flex-col flex-1 items-center justify-between"><img
                        :src="r(userProfile!.preferences.background.id)">
                </div>
                <div class="flex flex-col flex-1 items-center justify-between"><img
                        :src="r(userProfile!.preferences.frame.id)">
                </div>
                <div class="flex flex-col flex-1 items-center justify-between"><img
                        :src="r(userProfile!.preferences.character.id)">
                </div>
                <div class="flex flex-col flex-1 items-center justify-between"><img
                        :src="r(userProfile!.preferences.passname.id)">
                </div>
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
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">覆盖设置</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>玩家昵称</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖查分器返回的玩家昵称</span>
            </div>
            <div><input v-model="userProfile!.preferences.display_name"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>DX分数</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖查分器返回的DX分数</span>
            </div>
            <div><input v-model="userProfile!.preferences.dx_rating"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>人物名称</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面左下方的人物名称</span>
            </div>
            <div><input v-model="userProfile!.preferences.character_name"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>卡片号码</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面下方的20位号码</span>
            </div>
            <div><input v-model="userProfile!.preferences.simplified_code"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>游戏版本</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面下方的游戏版本</span>
            </div>
            <div><input v-model="userProfile!.preferences.maimai_version"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>角色框颜色</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面左下方的角色框颜色</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer -mr-1"
                    @click="() => userProfile!.preferences.chara_info_color = '#fee37c'">
                    <img src="../../assets/misc/refresh.svg">
                </a>
                <div class="color-preview mr-2"
                    :style="{ backgroundColor: userProfile!.preferences.chara_info_color || '#FFFFFF' }"></div>
                <input type="color" class="color-picker bg-white cursor-pointer"
                    v-model="userProfile!.preferences.chara_info_color">
            </div>
        </div>
    </div>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">账户绑定</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>
                    水鱼账户: <b>{{ userStore.userProfile!.accounts['1'] ? '已绑定' : '未绑定' }}
                        {{ userStore.userProfile!.prefer_server == 1 ? '(优先使用)' : '' }}</b>
                </span>
                <span class="text-gray-600" style="font-size: 12px;" v-if="userStore.userProfile!.accounts['1']">
                    DXRating: {{ userStore.userProfile!.accounts['1']?.player_rating }}
                </span>
            </div>
            <div class="flex items-center">
                <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mr-2"
                    v-if="userStore.userProfile!.prefer_server != 1 && userStore.userProfile!.accounts['1']"
                    @click="userStore.patchPreferServer(1)">
                    优先
                </button>
                <component :is="bindBtn(AccountServer.DIVINGFISH)"></component>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>
                    落雪账户: <b>{{ userStore.userProfile!.accounts['2'] ? '已绑定' : '未绑定' }}
                        {{ userStore.userProfile!.prefer_server == 2 ? '(优先使用)' : '' }}</b>
                </span>
                <span class="text-gray-600" style="font-size: 12px;" v-if="userStore.userProfile!.accounts['2']">
                    DXRating: {{ userStore.userProfile!.accounts['2']?.player_rating }}
                </span>
            </div>
            <div class="flex items-center">
                <div class="flex items-center">
                    <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600 mr-2"
                        v-if="userStore.userProfile!.prefer_server != 2 && userStore.userProfile!.accounts['2']"
                        @click="userStore.patchPreferServer(2)">
                        优先
                    </button>
                    <component :is="bindBtn(AccountServer.LXNS)"></component>
                </div>
            </div>
        </div>
    </div>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">自定义图片</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <input class="hidden" ref="image-picker" type="file" accept="image/jpeg,image/png,image/webp" />
            <div class="flex flex-col p-2">
                <span>上传背景</span>
                <span class="text-gray-600" style="font-size: 12px;">上传自定义背景图片 (768 * 1052)</span>
            </div>
            <div>
                <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                    @click="openPicker('background')">
                    上传
                </button>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>上传边框</span>
                <span class="text-gray-600" style="font-size: 12px;">上传自定义边框图片 (768 * 1052)</span>
            </div>
            <div>
                <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                    @click="openPicker('frame')">
                    上传
                </button>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>上传人物</span>
                <span class="text-gray-600" style="font-size: 12px;">上传自定义人物图片 (768 * 1052)</span>
            </div>
            <div>
                <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                    @click="openPicker('character')">
                    上传
                </button>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>上传PASS</span>
                <span class="text-gray-600" style="font-size: 12px;">上传自定义PASS图片 (338 * 112)</span>
            </div>
            <div>
                <button class="bg-orange-500 text-white font-bold py-2 px-4 rounded hover:bg-orange-600"
                    @click="openPicker('passname')">
                    上传
                </button>
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
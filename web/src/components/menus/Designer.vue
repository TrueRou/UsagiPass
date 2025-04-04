<script setup lang="ts">
import { useDraftStore } from '@/stores/draft';
import { useImageStore } from '@/stores/image';
import { useNotificationStore } from '@/stores/notification';
import { computed, ref, useTemplateRef } from 'vue';
import { useRouter } from 'vue-router';
import { useServerStore } from '@/stores/server';
import { useUserStore } from '@/stores/user';
import { Privilege, type Preference, type Kind, type Card } from '@/types';
import DXBaseView from '@/views/DXBaseView.vue';
import Prompt from '../widgets/Prompt.vue';
import { matchPhoneNumber } from '@/utils/formatUtils';
import { useCardStore } from '@/stores/card';


const props = defineProps<{
    uuid?: string;
}>()

const router = useRouter();
const draftStore = useDraftStore();
const cardStore = useCardStore();
const imageStore = useImageStore();
const userStore = useUserStore();
const serverStore = useServerStore();
const notificationStore = useNotificationStore();

const imagePicker = useTemplateRef('image-picker');
const showDialog = ref<boolean>(false);
const showBatchDialog = ref<boolean>(false);
const newDraftPhone = ref<string>(history.state.phoneNumber || '');
const batchCount = ref<number>(1);
const preferences = ref<Preference>(await draftStore.fetchPreferences(props.uuid));

const openPicker = (kind: Kind) => userStore.openImagePicker(kind, imagePicker.value!);

const openGallery = (kind: Kind) => {
    imageStore.wanderingPreferences = preferences.value;
    router.push({ name: 'gallery', params: { kind: kind } })
};

const openPhoneDialog = () => {
    if (!isAdmin.value && !newDraftPhone.value) showDialog.value = true;
    else createDraft();
}

const createDraft = async () => {
    if (await draftStore.testPreferences(preferences.value!)) {
        if (isAdmin.value) {
            await cardStore.createCard();
            router.push({ name: 'admin' });
            notificationStore.success("创建成功", "已成功创建一张卡片，卡片订单已自动付款");
            return;
        }
        else if (matchPhoneNumber(newDraftPhone.value)) {
            const card = await draftStore.createDraft(newDraftPhone.value);
            await draftStore.patchPreferences(card.uuid, preferences.value!);
            showDialog.value = false;
            router.replace({ name: "designer", params: { uuid: card.uuid } });
            notificationStore.success("创建成功", "您的卡面已创建\n在订单确认前，您可以随时修改卡面设置");
            router.push({ name: 'drafts', state: { phoneNumber: newDraftPhone.value } });
        }
    }
}

const updateDraft = async () => {
    if (isAdmin.value) {
        await cardStore.patchPreferences(props.uuid!, preferences.value!);
        router.push({ name: 'admin' });
    } else {
        await draftStore.patchPreferences(props.uuid!, preferences.value!);
        router.push({ name: 'drafts', state: { phoneNumber: newDraftPhone.value } });
    }
    notificationStore.success("保存成功", "卡面设置已更新");
}

const openBatchDialog = () => {
    if (isAdmin.value) {
        showBatchDialog.value = true;
    }
}

const createBatchCards = async () => {
    if (!isAdmin.value) return;

    const count = parseInt(batchCount.value.toString());
    if (isNaN(count) || count < 1 || count > 32) {
        notificationStore.error("数量错误", "批量创建数量必须在1-32之间");
        return;
    }

    try {
        for (let i = 0; i < count; i++) {
            const card: Card = await cardStore.createCard();
            await cardStore.patchPreferences(card.uuid, preferences.value!);
        }
        notificationStore.success("批量创建成功", `已成功创建${count}张卡片`);
        showBatchDialog.value = false;
        router.push({ name: 'admin' });
    } catch (error) {
        notificationStore.error("批量创建失败", "创建卡片时发生错误");
    }
}

const isAdmin = computed(() => userStore.userProfile?.privilege === Privilege.ADMIN);
const preferencesReadOnly = computed(() => JSON.parse(JSON.stringify(preferences.value)));
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">卡面预览</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>成品遵循: ISO 7810 ID-1 (85.60 x 53.98 mm)</span>
                <span class="text-gray-600" style="font-size: 12px;">下方预览的比例可能不是 100% 准确</span>
            </div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-1 preview-radius mr-5" style="zoom: 0.4;">
                <DXBaseView :preferences="preferencesReadOnly" :card-id="1000" />
            </div>
            <div class="flex flex-1 preview-radius" style="zoom: 0.4;">
                <DXBaseView :preferences="preferencesReadOnly" card-back :card-id="1000" />
            </div>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col flex-1 items-center justify-between">
                <p class="text-gray-600" style="font-size: 12px;">正面预览</p>
            </div>
            <div class="flex flex-col flex-1 items-center justify-between">
                <p class="text-gray-600" style="font-size: 12px;">背面预览</p>
            </div>
        </div>
    </div>
    <Prompt text="请输入您的手机号码: <br>  手机号码只用于跟踪和确认订单" v-model="newDraftPhone" :show="showDialog" @confirm="createDraft"
        @cancel="showDialog = false;">
    </Prompt>

    <Prompt text="请输入批量创建数量: <br> 一次最多可创建1-32张卡片" v-model="batchCount" :show="showBatchDialog"
        @confirm="createBatchCards" @cancel="showBatchDialog = false;" inputType="number">
    </Prompt>

    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">卡面设置</h1>
        </div>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>背景图片</span>
                <span class="text-gray-600" style="font-size: 12px;">选择卡面背景图片</span>
            </div>
            <div class="flex items-center">
                <a class="bg-blue-500 text-white font-bold h-[32px] w-[32px] p-2 rounded hover:bg-blue-600 text-sm cursor-pointer mr-1"
                    @click="openGallery('background')">
                    <img src="../../assets/misc/images.svg">
                </a>
                <select v-model="preferences!.background.id">
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
                <select v-model="preferences!.frame.id">
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
                <select v-model="preferences!.character.id">
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
                <select v-model="preferences!.passname.id">
                    <option v-for="item in imageStore.images?.passname" :value="item.id">{{ item.name }}</option>
                </select>
            </div>
        </div>
    </div>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">个人设置</h1>
        </div>
        <template v-if="isAdmin">
            <div class="flex justify-between items-center w-full">
                <div class="flex flex-col p-2">
                    <span>卡片元数据</span>
                    <span class="text-gray-600" style="font-size: 12px;">覆盖卡面左下方的CID</span>
                </div>
                <div><input v-model="preferences!.simplified_code" placeholder="默认情况请留空"></div>
            </div>
            <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        </template>
        <div class="flex justify-between items-center w-full mt-2">
            <div class="flex flex-col p-2">
                <span>玩家昵称</span>
                <span class="text-gray-600" style="font-size: 12px;">卡面印刷的玩家昵称</span>
            </div>
            <div><input v-model="preferences!.display_name" placeholder="留空隐藏姓名框"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>好友号码</span>
                <span class="text-gray-600" style="font-size: 12px;">卡面印刷的好友号码</span>
            </div>
            <div><input v-model="preferences!.friend_code" placeholder="留空隐藏好友代码"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>DX分数</span>
                <span class="text-gray-600" style="font-size: 12px;">卡面印刷的DX分数</span>
            </div>
            <div><input v-model="preferences!.dx_rating" placeholder="留空不印刷DX分数"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>人物名称</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面左下方的人物名称</span>
            </div>
            <div><input v-model="preferences!.character_name" :placeholder="preferences.character.name"></div>
        </div>
        <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
        <div class="flex justify-between items-center w-full">
            <div class="flex flex-col p-2">
                <span>游戏版本</span>
                <span class="text-gray-600" style="font-size: 12px;">覆盖卡面下方的游戏版本</span>
            </div>
            <div><input v-model="preferences!.maimai_version" :placeholder="serverStore.serverMessage?.maimai_version">
            </div>
        </div>
    </div>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full mt-2">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">自定义图片</h1>
        </div>
        <template v-if="userStore.isSignedIn">
            <div class="flex justify-between items-center w-full mt-2">
                <div class="flex items-center">
                    <img class="w-12 h-12 rounded-full ml-2" src="https://assets2.lxns.net/maimai/icon/300103.png">

                    <div class="flex flex-col p-2">
                        <span>
                            {{ userStore.preferAccount?.nickname }} ({{ userStore.userProfile!.username }})
                        </span>
                        <span class="text-gray-600" style="font-size: 12px;">
                            该账号仅用于上传自定义图片
                            DXRating: {{ userStore.preferAccount?.player_rating }}
                        </span>
                    </div>
                </div>
                <div class="flex items-center">
                    <a class="ml-2 bg-red-500 text-white font-bold py-1 px-1 h-[40px] w-[40px] rounded hover:bg-red-600 text-sm cursor-pointer"
                        @click="userStore.logout">
                        <img class="pl-1.5 pt-1" src="../../assets/misc/logout.svg">
                    </a>
                </div>
            </div>
            <div class="w-full border-t border-gray-300 mt-1 mb-1"></div>
            <div class="flex justify-between items-center w-full">
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
        </template>
        <template v-else>
            <div class="flex justify-between items-center w-full mt-2">
                <div class="flex flex-col p-2">
                    <span>登录以继续</span>
                    <span class="text-gray-600" style="font-size: 12px;">支持使用水鱼或落雪账户进行登录</span>
                </div>
                <div>
                    <RouterLink class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600"
                        :to="{ name: 'login', state: { useBack: true } }">
                        登录
                    </RouterLink>
                </div>
            </div>
        </template>
    </div>
    <div class="flex justify-end w-full mt-2 mr-5">
        <template v-if="props.uuid">
            <button class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-600"
                v-on:click="updateDraft">
                保存
            </button>
        </template>
        <template v-else>
            <button class="bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-600"
                v-on:click="openPhoneDialog">
                创建
            </button>
            <button v-if="isAdmin" class="bg-red-500 text-white font-bold py-2 px-4 ml-2 rounded hover:bg-red-600"
                v-on:click="openBatchDialog">
                批量创建
            </button>
        </template>
    </div>
</template>
<style scoped>
input {
    font-size: 14px;
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

.preview-radius {
    border-radius: 16px;
    mask-image: radial-gradient(circle, white 100%, black 100%);
    -webkit-mask-image: -webkit-radial-gradient(circle, white 100%, black 100%);
}
</style>
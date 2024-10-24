<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useServerStore } from '@/stores/server';
import DXRating from '@/components/DXRating.vue';
import QRCode from '@/components/QRCode.vue';
import CharaInfo from '@/components/CharaInfo.vue';
import PlayerInfo from '@/components/PlayerInfo.vue';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const serverStore = useServerStore();
const router = useRouter();
const userProfile = ref<UserProfile>(userStore.userProfile!);

const r = (resource_key: ImagePublic) => import.meta.env.VITE_URL + "/images/" + resource_key!.id;

const prepareDefaultPreferences = () => {
    userProfile.value!.preferences.character_name ||= userProfile.value!.preferences.character.name;
    userProfile.value!.preferences.display_name ||= userProfile.value!.nickname;
    userProfile.value!.preferences.dx_rating ||= userProfile.value!.player_rating;
    userProfile.value!.preferences.friend_code ||= "664994421382429"; // this is my friend code
    userProfile.value!.preferences.simplified_code ||= userStore.simplifiedCode;
    userProfile.value!.preferences.maimai_version ||= serverStore.serverMessage!.maimai_version;
}

prepareDefaultPreferences();

</script>
<template>
    <div class="flex items-center justify-center h-full w-full">
        <div class="flex relative flex-col items-center justify-center h-full">
            <img class="h-full object-cover -z-30" :src="r(userProfile?.preferences.background)">
            <img class="frame-upper h-full absolute -z-10" :src="r(userProfile?.preferences.frame)">
            <img class="frame-under h-full absolute -z-10" :src="r(userProfile?.preferences.frame)">
            <img class="chara-center absolute object-cover -z-20" :src="r(userProfile?.preferences.character)">
            <div class="flex flex-col absolute top-0 w-full h-full">
                <div class="header-widget flex relative w-full justify-between">
                    <img class="object-cover w-1/2" :src="r(userProfile?.preferences.passname)">
                    <DXRating class="w-1/2" :rating="userProfile.preferences.dx_rating || 0" />
                </div>
                <div class="header-widget flex relative w-full flex-row-reverse">
                    <PlayerInfo class="w-1/2" :username="userProfile.nickname"
                        :friend-code="userProfile.preferences.friend_code!" />
                </div>
            </div>
            <div class="absolute flex flex-col left-0" style="width: 50%; bottom: 8%;">
                <CharaInfo :chara="userProfile.preferences.character_name!" :time="userStore.timeLimit || '12:00:00'" />
            </div>
            <div class="qr-widget absolute" v-if="userStore.maimaiCode">
                <QRCode :content="userStore.maimaiCode" :size="userProfile.preferences.qr_size || 20" />
            </div>
            <div class="flex absolute bottom-0 items-center justify-center w-full h-8">
                <div class="footer-widget flex justify-between py-1 rounded-2xl bg-gray-800 text-white opacity-85">
                    <p class="footer-text">{{ userProfile.preferences.simplified_code }}</p>
                    <p class="footer-text">{{ userProfile.preferences.maimai_version }}</p>
                </div>
                <div class="p-1 rounded-full bg-white" @click="router.push({ name: 'settings' })">
                    <img src="../assets/misc/settings.svg" style="width: 2vh;"></img>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
.frame-upper {
    object-fit: contain;
    object-position: left top;
    clip-path: polygon(0 0, 100% 0, 100% 50%, 0 50%);
}

.frame-under {
    object-fit: contain;
    object-position: left bottom;
    clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%);
}

.chara-center {
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%)
}

.qr-widget {
    bottom: 5%;
    right: 0;
}

.header-widget {
    padding-left: 2%;
    padding-right: 2%;
    padding-top: 0.4%;
}

.footer-widget {
    width: 85%;
    padding-left: 3%;
    padding-right: 3%;
}

.footer-text {
    font-size: 1.2vh;
    font-family: FOTSeurat;
    line-height: 120%;
}
</style>
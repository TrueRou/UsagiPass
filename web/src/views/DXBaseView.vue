<script setup lang="ts">
import { useRouter } from 'vue-router';
import DXRating from '@/components/DXRating.vue';
import QRCode from '@/components/QRCode.vue';
import CharaInfo from '@/components/CharaInfo.vue';
import PlayerInfo from '@/components/PlayerInfo.vue';
import CardBack from '@/components/CardBack.vue';
import { useServerStore } from '@/stores/server';
import { watch } from 'vue';

const props = defineProps<{
    preferences: PreferencePublic;
    timeLimit?: string;
    maimaiCode?: string;
    settingsRoute?: string;
}>()

const router = useRouter();
const serverStore = useServerStore();

const r = (image: ImagePublic) => import.meta.env.VITE_URL + "/images/" + image!.id;

const applyPreferences = () => {
    props.preferences.character_name ||= props.preferences.character.name;
    props.preferences.maimai_version ||= serverStore.serverMessage!.maimai_version;
}

watch(() => props.preferences, applyPreferences, { immediate: true });
</script>
<template>
    <div class="flex items-center justify-center h-full w-full">
        <div class="flex relative flex-col items-center justify-center h-full">
            <CardBack :preferences="preferences" />
            <div class="flex flex-col absolute top-0 w-full h-full">
                <div class="header-widget flex relative w-full justify-between">
                    <img class="object-cover w-1/2" :src="r(preferences.passname)">
                    <DXRating class="w-1/2" :rating="Number(preferences.dx_rating) || 0" />
                </div>
                <div class="header-widget flex relative w-full flex-row-reverse">
                    <PlayerInfo class="w-1/2" :username="preferences.display_name!"
                        :friend-code="preferences.friend_code!" />
                </div>
            </div>
            <div class="absolute flex flex-col left-0" style="bottom: 8%;">
                <CharaInfo :chara="preferences.character_name!" :time="timeLimit || '12:00:00'" />
            </div>
            <div class="qr-widget absolute" v-if="maimaiCode">
                <QRCode :content="maimaiCode" :size="preferences.qr_size || 20" />
            </div>
            <div class="flex absolute bottom-0 items-center justify-center w-full h-8">
                <div class="footer-widget flex justify-between py-1 rounded-2xl bg-gray-800 text-white opacity-85">
                    <p class="footer-text font-sega">{{ preferences.simplified_code }}</p>
                    <p class="footer-text font-sega">{{ preferences.maimai_version }}</p>
                </div>
                <template v-if="settingsRoute">
                    <div class="p-1 rounded-full bg-white" @click="router.push({ name: settingsRoute })">
                        <img src="../assets/misc/settings.svg" style="width: 2vh;"></img>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>
<style scoped>
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
    line-height: 120%;
}
</style>
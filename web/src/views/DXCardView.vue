<script setup lang="ts">
import { ref } from 'vue';
import { useCardStore } from '@/stores/card';
import { useServerStore } from '@/stores/server';
import DXRating from '@/components/DXRating.vue';
import CharaInfo from '@/components/CharaInfo.vue';
import PlayerInfo from '@/components/PlayerInfo.vue';
import { useRouter } from 'vue-router';
import CardBack from '@/components/CardBack.vue';

const props = defineProps<{
    uuid: string;
}>()

const cardStore = useCardStore();
const serverStore = useServerStore();
const router = useRouter();
const cardProfile = ref<CardProfile>(await cardStore.fetchCard(props.uuid));

const r = (image: ImagePublic) => import.meta.env.VITE_URL + "/images/" + image!.id;

const prepareDefaultPreferences = () => {
    cardProfile.value!.preferences.character_name ||= cardProfile.value!.preferences.character.name;
    cardProfile.value!.preferences.display_name ||= cardProfile.value!.preferences.display_name;
    cardProfile.value!.preferences.dx_rating ||= String(cardProfile.value.player_rating) || String(cardProfile.value!.player_rating);
    cardProfile.value!.preferences.maimai_version ||= serverStore.serverMessage!.maimai_version;
}

prepareDefaultPreferences();

</script>
<template>
    <div class="flex items-center justify-center h-full w-full">
        <div class="flex relative flex-col items-center justify-center h-full">
            <CardBack :preferences="cardProfile?.preferences" />
            <div class="flex flex-col absolute top-0 w-full h-full">
                <div class="header-widget flex relative w-full justify-between">
                    <img class="object-cover w-1/2" :src="r(cardProfile?.preferences.passname)">
                    <DXRating class="w-1/2" :rating="Number(cardProfile?.preferences.dx_rating) || 0" />
                </div>
                <div class="header-widget flex relative w-full flex-row-reverse">
                    <PlayerInfo class="w-1/2" :username="cardProfile?.preferences.display_name!"
                        :friend-code="cardProfile?.preferences.friend_code!" />
                </div>
            </div>
            <div class="absolute flex flex-col left-0" style="bottom: 8%;">
                <CharaInfo :chara="cardProfile?.preferences.character_name!" :time="'12:00:00'" />
            </div>
            <div class="flex absolute bottom-0 items-center justify-center w-full h-8">
                <div class="footer-widget flex justify-between py-1 rounded-2xl bg-gray-800 text-white opacity-85">
                    <p class="footer-text font-sega">{{ cardProfile?.preferences.simplified_code }}</p>
                    <p class="footer-text font-sega">{{ cardProfile?.preferences.maimai_version }}</p>
                </div>
                <div class="p-1 rounded-full bg-white" @click="router.push({ name: 'preferences' })">
                    <img src="../assets/misc/settings.svg" style="width: 2vh;"></img>
                </div>
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
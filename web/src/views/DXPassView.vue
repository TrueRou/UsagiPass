<script setup lang="ts">
import { ref, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import type { Preference } from '@/types';
import DXBaseView from './DXBaseView.vue';


const userStore = useUserStore();
const preferences = ref<Preference>(JSON.parse(JSON.stringify(userStore.userProfile!.preferences)));

const applyPreferences = () => {
    preferences.value.display_name ||= userStore.userProfile!.nickname;
    preferences.value.dx_rating ||= String(userStore.userProfile!.player_rating);
    preferences.value.friend_code ||= "664994421382429"; // this is my friend code
    preferences.value.simplified_code ||= userStore.simplifiedCode;
}

watch(() => preferences, applyPreferences, { immediate: true });
</script>
<template>
    <DXBaseView :preferences="preferences" :timeLimit="userStore.timeLimit" :maimaiCode="userStore.maimaiCode"
        :settingsRoute="{ name: 'preferencesPass' }" />
</template>

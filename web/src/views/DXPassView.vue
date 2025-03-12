<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import DXBaseView from './DXBaseView.vue';

const userStore = useUserStore();
const preferences = ref<PreferencePublic>(JSON.parse(JSON.stringify(userStore.userProfile!.preferences))); // Deep copy

const applyPreferences = () => {
    preferences.value.display_name ||= userStore.userProfile!.nickname;
    preferences.value.dx_rating ||= String(userStore.userProfile!.player_rating);
    preferences.value.friend_code ||= "664994421382429"; // this is my friend code
    preferences.value.simplified_code ||= userStore.simplifiedCode;
}

applyPreferences();
</script>
<template>
    <DXBaseView :preferences="preferences" :timeLimit="userStore.timeLimit" :maimaiCode="userStore.maimaiCode"
        settingsRoute="preferences" />
</template>

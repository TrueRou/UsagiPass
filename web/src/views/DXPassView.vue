<script setup lang="ts">
import { ref, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { AccountServer, type Preference } from '@/types';
import DXBaseView from './DXBaseView.vue';


const userStore = useUserStore();
const preferences = ref<Preference>(JSON.parse(JSON.stringify(userStore.userProfile!.preferences)));

const applyPreferences = () => {
    preferences.value.display_name ||= userStore.preferAccount!.nickname;
    preferences.value.dx_rating ||= String(userStore.preferAccount!.player_rating);
    preferences.value.simplified_code ||= userStore.simplifiedCode;
    if (userStore.userProfile?.prefer_server === AccountServer.WECHAT) {
        preferences.value.friend_code ||= userStore.preferAccount!.account_name;
    }
}

watch(() => preferences, applyPreferences, { immediate: true });
</script>
<template>
    <DXBaseView :preferences="preferences" :timeLimit="userStore.timeLimit" :maimaiCode="userStore.maimaiCode"
        :settingsRoute="{ name: 'preferencesPass' }" />
</template>

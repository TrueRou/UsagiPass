<script setup lang="ts">
import { ref } from 'vue';
import { useCardStore } from '@/stores/card';
import DXBaseView from './DXBaseView.vue';
import type { CardProfile, PreferencePublic } from '@/types';

const props = defineProps<{
    uuid: string;
}>()

const cardStore = useCardStore();
const cardProfile = ref<CardProfile>(await cardStore.fetchCard(props.uuid));
const cardPreference = ref<PreferencePublic>(JSON.parse(JSON.stringify(cardProfile.value!.preferences))); // Deep copy

const applyPreferences = () => {
    cardPreference.value.dx_rating ||= String(cardProfile.value.player_rating);
}

applyPreferences();
</script>
<template>
    <DXBaseView :preferences="cardPreference" timeLimit="12:00:00" :maimaiCode="undefined"
        settingsRoute="preferences" />
</template>
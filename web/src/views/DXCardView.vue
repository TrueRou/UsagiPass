<script setup lang="ts">
import { ref } from 'vue';
import { useCardStore } from '@/stores/card';
import { useServerStore } from '@/stores/server';
import DXBaseView from './DXBaseView.vue';

const props = defineProps<{
    uuid: string;
}>()

const cardStore = useCardStore();
const serverStore = useServerStore();
const cardProfile = ref<CardProfile>(await cardStore.fetchCard(props.uuid));
const cardPreference = ref<PreferencePublic>(JSON.parse(JSON.stringify(cardProfile.value!.preferences))); // Deep copy

const applyPreferences = () => {
    cardPreference.value.character_name ||= cardPreference.value.character.name;
    cardPreference.value.dx_rating ||= String(cardProfile.value.player_rating);
    cardPreference.value.maimai_version ||= serverStore.serverMessage!.maimai_version;
}

applyPreferences();

</script>
<template>
    <DXBaseView :preferences="cardPreference" timeLimit="12:00:00" :maimaiCode="null" settingsRoute="preferences" />
</template>
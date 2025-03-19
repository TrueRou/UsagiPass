<script setup lang="ts">
import { useCardStore } from '@/stores/card';
import { useRouter } from 'vue-router';

const props = defineProps<{
    uuid: string;
}>()

const router = useRouter();
const cardStore = useCardStore();

if (props.uuid !== cardStore.cardUUID) await cardStore.refreshCard(props.uuid)
router.replace({ name: 'cards', state: { "cardUUID": props.uuid } });
</script>
<template>

</template>
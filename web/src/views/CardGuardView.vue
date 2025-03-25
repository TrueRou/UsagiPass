<script setup lang="ts">
import { useCardStore } from '@/stores/card';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps<{
    uuid: string;
}>()

const route = useRoute();
const router = useRouter();
const cardStore = useCardStore();

if (props.uuid !== cardStore.cardUUID) await cardStore.refreshCard(props.uuid)
router.replace({ name: 'cards', state: { "cardUUID": props.uuid, "publish": route.query.publish || false, "back": route.query.back || false } });
</script>
<template>

</template>
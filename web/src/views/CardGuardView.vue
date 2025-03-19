<script setup lang="ts">
import { useRouter } from 'vue-router';

const props = defineProps<{
    uuid: string;
}>()

const router = useRouter();
router.replace({ name: 'cards', state: { uuid: props.uuid } });
</script>
<template>

</template>
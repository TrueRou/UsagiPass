<script setup lang="ts">
import { computed, ref } from 'vue';
import { useServerStore } from '@/stores/server';
import type { Image, Preference } from '@/types';

const props = defineProps<{
    preferences: Preference;
}>()

const mask = ref<Image | undefined>(undefined);
const maskEnabled = computed(() => mask.value !== undefined)
const r = (image?: Image) => import.meta.env.VITE_URL + "/images/" + image?.id;

if (props.preferences.mask_type !== 0) {
    const serverStore = useServerStore();
    const response = await serverStore.axiosInstance.get(`/images/${props.preferences.character.id}/related`);
    mask.value = (response.data as Image[]).filter(image => image.kind === 'mask').pop();
}
</script>
<template>
    <img class="h-full object-cover -z-[20]" :src="r(props.preferences.background)">
    <div v-if="maskEnabled" class="lazer-mask h-full w-full absolute -z-[10]" :style="{ maskImage: `url(${r(mask)})` }">
        <div class="h-full w-full flow-colorful"></div>
    </div>
    <img class="chara-center h-full absolute object-cover -z-[15]" :src="r(props.preferences.character)">
    <img class="frame-upper h-full absolute -z-[5]" :src="r(props.preferences.frame)">
    <img class="frame-under h-full absolute -z-[5]" :src="r(props.preferences.frame)">
</template>
<style scoped>
.frame-upper {
    object-fit: contain;
    object-position: left top;
    clip-path: polygon(0 0, 100% 0, 100% 50%, 0 50%);
}

.frame-under {
    object-fit: contain;
    object-position: left bottom;
    clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%);
}

.chara-center {
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%)
}

.lazer-mask {
    mask-mode: alpha;
    mask-repeat: no-repeat;
    mask-size: cover;
    mask-position: center;
}

.flow-colorful {
    background: linear-gradient(to bottom right, red, yellow, blue);
    animation: hue 4s linear infinite;
}

@keyframes hue {
    from {
        filter: hue-rotate(0deg);
    }

    to {
        filter: hue-rotate(360deg);
    }
}
</style>
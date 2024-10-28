<script setup lang="ts">
const props = defineProps<{
    preferences: UserPreferencePublic;
}>()

const r = (resource_key: ImagePublic) => import.meta.env.VITE_URL + "/images/" + resource_key!.id;
</script>
<template>
    <img class="h-full object-cover -z-[20]" :src="r(props.preferences.background)">
    <div class="lazer-mask h-full w-full absolute -z-[15]">
        <!-- <div class="h-full w-full flow-colorful"></div> -->
    </div>
    <img class="chara-center h-full absolute object-cover -z-[10]" :src="r(props.preferences.character)">
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
    mask-image: #000;
    /* mask image here */
    mask-mode: luminance;
    mask-repeat: no-repeat;
    mask-size: cover;
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
<script setup lang="ts">
import { computed } from 'vue';

const ratingLevels = [
    1000,
    2000,
    4000,
    7000,
    10000,
    12000,
    13000,
    14000,
    14500,
    15000,
]

const props = defineProps<{
    rating: number;
}>()

const getNum = (id: string) => new URL(`../assets/rating/num/UI_CMN_Num_26p_${id}.png`, import.meta.url).href;
const getBase = (id: string) => new URL(`../assets/rating/UI_CMA_Rating_Base_${id}.png`, import.meta.url).href;

const numImages = computed(() => {
    const arr = String(props.rating).split('')
    while (arr.length < 5) arr.unshift('10');
    return arr.map(num => getNum(num));
})

const baseImage = computed(() => {
    var rating = props.rating;
    rating = Math.max(ratingLevels[0], Math.min(rating, ratingLevels[9]));
    let stage = 0;
    while (rating >= ratingLevels[stage + 1]) stage++;
    return getBase(String(stage + 1));
})
</script>
<template>
    <div class="relative">
        <div class="w-full">
            <img class="object-cover w-full" :src="baseImage">
        </div>
        <div class="flex absolute" style="right: 48%; top: 26%; width: 11%;">
            <img class="object-cover" v-for="path in numImages" :src="path">
        </div>
    </div>
</template>
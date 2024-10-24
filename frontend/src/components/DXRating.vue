<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';

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

const canvasRef = ref<HTMLCanvasElement | null>(null);

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

const drawCanvas = async () => {
    const scale = 0.8;
    const canvas = canvasRef.value;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const baseImg = new Image();
    baseImg.src = baseImage.value;
    await baseImg.decode();

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(baseImg, 0, 0, canvas.width, canvas.height);

    const numImgPromises = numImages.value.map(src => {
        const img = new Image();
        img.src = src;
        return img.decode().then(() => img);
    });

    const numImgs = await Promise.all(numImgPromises);
    numImgs.forEach((img, index) => {
        ctx.drawImage(img, 115 + index * 28, 20, 34 * scale, 40 * scale);
    });
}

onMounted(drawCanvas);
watch([baseImage, numImages], drawCanvas);
</script>

<template>
    <div class="relative">
        <canvas ref="canvasRef" width="269" height="70" class="w-full"></canvas>
    </div>
</template>
<script setup lang="ts">

const props = defineProps<{
    chara: string;
    time: string;
    date?: string;
    charaInfoColor?: string;
    showDate?: boolean;
}>()

</script>
<template>
    <div class="flex flex-col">
        <div class="flex flex-col pt-1 pb-1 rounded-tr-lg w-4/5" :style="{ 'background-color': charaInfoColor }">
            <p class="text-center text-sm font-semibold text-nowrap font-sega">{{ props.chara }}</p>
        </div>
        <div class="flex flex-col pb-1 rounded-tr-lg rounded-br-lg shadow-xl px-4"
            :style="{ 'background-color': charaInfoColor }">
            <p class="text-center text-nowrap text-sm font-sega">
                ブ一スト期限
                <b class="text-lg">{{ props.time }}</b>
            </p>
            <p v-if="props.showDate && props.date" class="text-center text-nowrap text-sm font-sega">
                <b class="text-lg">{{ props.date }}</b>
            </p>
        </div>
    </div>
</template>
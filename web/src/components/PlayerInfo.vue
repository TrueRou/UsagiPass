<script setup lang="ts">

const props = defineProps<{
    username?: string;
    friendCode?: string;
}>()

</script>
<template>
    <div class="bg-white right-0 flex flex-col rounded-md" v-if="props.username">
        <div class="flex items-center p-1">
            <p class="font-bold font-sega" style="font-size: 2.6vh;">{{ props.username }}</p>
            <img style="height: 3.5vh;" src="../assets/misc/UI_CMN_Name_DX.png">
        </div>
        <div class="flex items-center" v-if="props.friendCode">
            <p class="text-white pl-2 pr-2 text-center font-extrabold rounded-bl-md text-nowrap font-sega"
                style="font-size: 1.2vh; background-color: #405baa; -webkit-text-stroke: 1px #fff">
                フレンド<br>コ一ド
            </p>
            <p class="ml-0.5 font-extrabold font-sega" style="font-size: 1.8vh;">{{ props.friendCode }}
            </p>
        </div>
    </div>
</template>
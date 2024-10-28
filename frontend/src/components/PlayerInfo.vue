<script setup lang="ts">

const props = defineProps<{
    username: string;
    friendCode: string;
}>()

</script>
<template>
    <div class="bg-white right-0 flex flex-col rounded-md">
        <div class="flex items-center p-1">
            <p class="font-bold" style="font-size: 3vh;">{{ props.username }}</p>
            <img style="height: 3.5vh;" src="../assets/misc/UI_CMN_Name_DX.png">
        </div>
        <div class="flex items-center">
            <p class="text-white pl-2 pr-2 text-center font-extrabold rounded-bl-md text-nowrap"
                style="font-size: 1vh; background-color: #405baa; -webkit-text-stroke: 1px #fff">
                フレンド<br>コ一ド
            </p>
            <p class="ml-0.5 font-bold" style="font-size: 1.6vh;">{{ props.friendCode }}
            </p>
        </div>
    </div>
</template>
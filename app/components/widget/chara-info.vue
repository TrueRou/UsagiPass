<script setup lang="ts">
const props = defineProps<{
    charaName?: string
    timeLimit?: string
    dateLimit?: string
    charaInfoColor?: string
    showDate?: boolean
}>()
</script>

<template>
    <div class="flex flex-col text-black">
        <div v-if="props.charaName" class="flex flex-col pt-1 pb-1 rounded-tr-lg w-4/5" :style="{ 'background-color': charaInfoColor }">
            <p class="text-center text-sm font-semibold text-nowrap font-sega">
                {{ props.charaName }}
            </p>
        </div>
        <div
            class="flex flex-col pb-1 rounded-tr-lg rounded-br-lg shadow-xl px-4"
            :style="{ 'background-color': charaInfoColor }"
        >
            <p class="text-center text-nowrap font-sega">
                <span class="text-sm mr-1">ブ一スト期限</span>
                <b class="text-md">{{ props.timeLimit || '12:00:00' }}</b>
            </p>
            <p v-if="props.showDate && props.dateLimit" class="text-center text-md text-nowrap font-sega">
                <b>{{ props.dateLimit }}</b>
            </p>
        </div>
    </div>
</template>

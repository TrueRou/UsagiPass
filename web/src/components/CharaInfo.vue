<script setup lang="ts">

const props = defineProps<{
    cardId?: number;
    chara: string;
    time: string;
}>()

</script>
<template>
    <div class="flex flex-col">
        <div class="flex flex-col pt-1 pb-1 rounded-tr-lg" style="width: 80%; background-color: #fee37c;">
            <p class="text-center text-sm font-semibold text-nowrap font-sega">{{ props.chara }}</p>
        </div>
        <div class="flex flex-col pb-1 rounded-tr-lg rounded-br-lg shadow-xl px-4" style="background-color: #fee37c;">
            <p class="text-center text-nowrap text-sm font-sega">
                <template v-if="cardId">
                    カード 番号
                    <b class="text-lg">{{ props.cardId }}</b>
                </template>
                <template v-else>
                    ブ一スト期限
                    <b class="text-lg">{{ props.time }}</b>
                </template>
            </p>
        </div>
    </div>
</template>
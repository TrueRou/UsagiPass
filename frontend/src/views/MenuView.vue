<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const images = ref<Record<string, ImageDetail[]>>()

const response = await userStore.axiosInstance.get('/bits/')
images.value = response.data.reduce((acc: Record<string, ImageDetail[]>, item: ImageDetail) => {
    if (!acc[item.kind]) {
        acc[item.kind] = [];
    }
    acc[item.kind].push(item);
    return acc;
}, {});
</script>
<template>
    <div class="bg-blue-400 flex flex-col items-center h-full w-full">
        <div class="flex flex-col items-center h-full w-full sm:w-[640px] pl-4 pr-4 pt-2 pb-2">
            <div class="flex flex-col items-center h-full w-full rounded bg-white p-4 overflow-y-scroll">
                <RouterView :images="images" /> <!-- It's not a good idea to passthrough props like this. -->
            </div>
        </div>
    </div>
</template>
<style scoped>
::-webkit-scrollbar {
    display: none;
}
</style>
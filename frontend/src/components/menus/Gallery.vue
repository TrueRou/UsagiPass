<script setup lang="ts">
import { useImageStore } from '@/stores/image';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const props = defineProps<{
    kind: string;
}>()

const kindDict: Record<string, string> = {
    'background': '背景',
    'character': '角色',
    'frame': '边框',
    'passname': '通行证',
}

const userStore = useUserStore();
const imageStore = useImageStore();
const router = useRouter();
const { userProfile } = storeToRefs(userStore)

const r = (resource_id: string) => import.meta.env.VITE_URL + `/images/${resource_id}/thumbnail`;

const selectImage = (image: ImagePublic) => {
    (userProfile.value?.preferences as any)[props.kind].id = image.id;
    router.push({ name: "preferences" });
}

const deleteImage = async (image: ImagePublic) => {
    if (confirm(`确定删除 ${image.name} 吗？`)) {
        await userStore.axiosInstance.delete("/images/" + image.id)
        await imageStore.refreshImages();
    }
}

const renameImage = async (image: ImagePublic) => {
    const name = prompt("请输入新的名称", image.name);
    if (name) {
        await userStore.axiosInstance.patch("/images/" + image.id + "?name=" + name);
        await imageStore.refreshImages();
    }
}

if (!imageStore.images) await imageStore.refreshImages();

if (!Object.keys(imageStore.images!).includes(props.kind)) {
    alert(`访问的资源 ${props.kind} 不存在`)
    router.push({ name: 'home' }); // Redirect to home page
}
</script>
<template>
    <div class="flex flex-col items-center rounded border-solid border-2 shadow-lg border-black p-2 w-full">
        <div class="flex items-center justify-center bg-blue-400 w-full rounded h-8">
            <h1 class="font-bold text-white">{{ '选取' + kindDict[props.kind] }}</h1>
        </div>
        <div class="grid grid-cols-3 gap-4 mt-2">
            <template v-for="image in imageStore.images![props.kind]">
                <div class="relative rounded border-solid border-2 shadow-lg border-black p-2">
                    <button
                        class="absolute top-0 left-0 bg-black bg-opacity-50 text-white p-1 rounded-br-lg text-xs max-w-full z-10"
                        v-if="image.uploaded_by" @click="renameImage(image)">
                        {{ image.name }}
                    </button>
                    <div class="absolute top-0 left-0 bg-black bg-opacity-50 text-white p-1 rounded-br-lg text-xs max-w-full z-10"
                        v-else>
                        {{ image.name }}
                    </div>
                    <img :src="r(image.id)" class="w-full h-48 object-contain rounded-lg">
                    <button
                        class="absolute top-0 right-0 bg-black bg-opacity-50 text-white p-1 rounded-bl-lg text-xs max-w-full z-10"
                        @click="deleteImage(image)" v-if="image.uploaded_by">
                        删除
                    </button>
                    <button
                        class="absolute inset-0 bg-black bg-opacity-50 text-white flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity"
                        @click="selectImage(image)">
                        选择
                    </button>
                </div>
            </template>
        </div>
    </div>
</template>
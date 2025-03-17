<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { onMounted, ref, useTemplateRef } from 'vue';
import { VueCropper } from "vue-cropper";
import { useServerStore } from '@/stores/server';
import { useRouter } from 'vue-router';
import { useImageStore } from '@/stores/image';
import 'vue-cropper/dist/index.css'
import Prompt from '@/components/widgets/Prompt.vue';

const props = defineProps<{
    kind: string;
}>()

const router = useRouter();
const userStore = useUserStore();
const imageStore = useImageStore();
const serverStore = useServerStore();

const imageCropper = useTemplateRef('cropper');
const fixedNumber = ref<Array<number>>([0, 0]);
const showDialog = ref<boolean>(false);
const imageName = ref<string>('');

const uploadImage = async () => {
    ((imageCropper.value) as any).getCropBlob(async (blob: Blob) => {
        imageStore.uploadImage(props.kind, imageName.value, blob);
    });
}

onMounted(async () => {
    if (!serverStore.serverKinds) await serverStore.refreshKind()
    fixedNumber.value = serverStore.serverKinds![props.kind]["hw"][0]
    if (!Object.keys(serverStore.serverKinds!).includes(props.kind)) {
        alert(`访问的资源 ${props.kind} 不存在`)
        router.back();
    }
})
</script>
<template>
    <Prompt text="请输入图片名称: " v-model="imageName" :show="showDialog" @confirm="uploadImage"
        @cancel="showDialog = false;"></Prompt>
    <div class="cropper-frame">
        <VueCropper ref="cropper" :img="userStore.cropperImage" :outputSize="1" outputType="png" :autoCrop="true"
            :fixed="true" :fixedNumber="fixedNumber" :autoCropWidth="fixedNumber![0]" :autoCropHeight="fixedNumber![1]"
            :infoTrue="true" :full="true">
        </VueCropper>
    </div>
    <button
        class="absolute flex bottom-5 left-1/2 -translate-x-1/2 rounded-full h-16 w-16 bg-blue-500 hover:bg-blue-700 justify-center items-center"
        @click="showDialog = true;">
        <span class="-mt-2 text-2xl">📷</span>
    </button>
</template>
<style scoped>
.cropper-frame {
    width: 100%;
    height: 100%;
}
</style>
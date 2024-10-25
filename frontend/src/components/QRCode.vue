<script setup lang="ts">
import QRCode, { type QRCodeToDataURLOptions } from 'qrcode'
import { useTemplateRef, watchEffect } from 'vue';

const qrcodeOpts = {
    errorCorrectionLevel: 'L',
    type: 'image/jpeg',
    quality: 0.3,
    margin: 1
} as QRCodeToDataURLOptions

const props = defineProps<{
    content?: string | null;
    size: number;
}>()

const qrImage = useTemplateRef('qr-image')

watchEffect(() => {
    if (qrImage.value && props.content) {
        QRCode.toDataURL("SGWC" + props.content, qrcodeOpts, (err, url) => {
            if (err) console.error(err)
            qrImage.value!.src = url
        })
    }
})
</script>
<template>
    <div class="p-0.5 rounded bg-white">
        <img class="w-full h-full" ref="qr-image" :style="{ width: `${size}vh` }"></img>
    </div>
</template>
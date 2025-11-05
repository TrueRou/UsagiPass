<script setup lang="ts">
import type { QRCodeToDataURLOptions } from 'qrcode'
import QRCode from 'qrcode'

const props = defineProps<{
    content?: string | null
    size: string | number
}>()

const qrcodeOpts = {
    errorCorrectionLevel: 'L',
    type: 'image/jpeg',
    quality: 0.3,
    margin: 1,
} as QRCodeToDataURLOptions

const qrImage = useTemplateRef('qr-image')

watchEffect(() => {
    if (qrImage.value && props.content) {
        QRCode.toDataURL(`SGWC${props.content}`, qrcodeOpts, (err: any, url: any) => {
            if (err)
                console.error(err)
            qrImage.value!.src = url
        })
    }
})
</script>

<template>
    <div v-if="Number(size) !== -1" class="p-0.5 rounded bg-white">
        <img ref="qr-image" class="w-full h-full" :style="{ width: `${size}vh` }">
    </div>
</template>

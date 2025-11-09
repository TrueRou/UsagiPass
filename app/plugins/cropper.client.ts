import VueCropper from 'vue-cropper'
import 'vue-cropper/dist/index.css'

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.use(VueCropper as any)
})

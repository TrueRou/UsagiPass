// vue-cropper 的 lib/index.ts 以源码形式发布并引用同目录的 .vue 文件，类型检查时需要声明
declare module '*/vue-cropper.vue' {
    import type { DefineComponent } from 'vue'

    const component: DefineComponent
    export default component
}

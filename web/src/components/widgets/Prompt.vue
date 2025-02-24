<script setup lang="ts">
const model = defineModel()
const props = defineProps(['text', 'show'])
const emits = defineEmits(['confirm', 'cancel'])
</script>
<template>
    <div v-if="props.show" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-20">
        <div class="bg-white p-4 rounded shadow-lg">
            <label for="imageName" class="block text-md font-bold text-gray-700">{{ props.text }}</label>
            <input v-model="model" type="text"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
            <div class="mt-2 flex justify-end">
                <button @click="emits('confirm')"
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">确定</button>
                <button @click="emits('cancel')"
                    class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded ml-2">取消</button>
            </div>
        </div>
    </div>
</template>
<style scoped>
input {
    outline-style: none;
    border: 2px solid #000;
    border-radius: 5px;
    width: 200px;
    height: 44.5px;
    padding: 0;
    padding: 10px 10px;
    box-sizing: border-box;

    &:focus {
        border-color: #60a5fa;
        outline: 0;
        -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
        box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075),
            #60a5fa;
    }
}
</style>
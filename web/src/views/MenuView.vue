<template>
    <div class="bg-blue-400 flex flex-col items-center h-full w-full">
        <div class="flex flex-col items-center h-full w-full sm:w-[640px] pl-4 pr-4 pt-2 pb-2">
            <div
                class="flex flex-col items-center h-full w-full rounded bg-white p-4 overflow-y-scroll overflow-x-hidden">
                <RouterView />
            </div>
        </div>
    </div>
</template>
<style scoped>
::-webkit-scrollbar {
    display: none;
}
</style>
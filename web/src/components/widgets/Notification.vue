<script setup lang="tsx">
import { useNotificationStore, type NotificationType } from '@/stores/notification';
import { ref, computed } from 'vue';

const notificationStore = useNotificationStore();
const isVisible = ref(true);

const getBackgroundColor = (type: NotificationType) => {
    switch (type) {
        case 'success':
            return 'bg-green-50 border-green-200';
        case 'warning':
            return 'bg-yellow-50 border-yellow-200';
        case 'error':
            return 'bg-red-50 border-red-200';
        default:
            return 'bg-blue-50 border-blue-200';
    }
};

const getIconClasses = (type: NotificationType) => {
    switch (type) {
        case 'success':
            return 'text-green-500';
        case 'warning':
            return 'text-yellow-500';
        case 'error':
            return 'text-red-500';
        default:
            return 'text-blue-500';
    }
};

const getIcon = (type: NotificationType) => {
    switch (type) {
        case 'success':
            return (
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
            );
        case 'warning':
            return (
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            );
        case 'error':
            return (
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            );
        default:
            return (
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            );
    }
};

const isMobile = computed(() => {
    return window.innerWidth < 640;
});
</script>

<template>
    <div v-if="isVisible" aria-live="assertive"
        class="notification-container fixed inset-0 flex px-4 py-6 pointer-events-none z-50">
        <div class="w-full flex flex-col items-center space-y-4 sm:items-end">
            <template v-for="notification in notificationStore.notifications" :key="notification.id">
                <div :class="[
                    'max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto border-l-4 transform transition-all duration-300',
                    getBackgroundColor(notification.type),
                    isMobile ? 'mx-auto' : ''
                ]" :style="{
                    animation: 'notification-slide-in 0.3s ease-out forwards'
                }">
                    <div class="p-4">
                        <div class="flex items-start">
                            <div :class="['flex-shrink-0', getIconClasses(notification.type)]">
                                <component :is="getIcon(notification.type)" />
                            </div>
                            <div class="ml-3 w-0 flex-1 pt-0.5">
                                <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
                                <p class="mt-1 text-sm text-gray-500" :style="{ whiteSpace: 'pre-line' }">{{
                                    notification.message }}</p>
                            </div>
                            <div class="ml-4 flex-shrink-0 flex">
                                <button type="button" @click="notificationStore.remove(notification.id)"
                                    class="rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    <span class="sr-only">关闭</span>
                                    <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
                                        fill="currentColor" aria-hidden="true">
                                        <path fill-rule="evenodd"
                                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                            clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<style scoped>
@keyframes notification-slide-in {
    0% {
        transform: translateX(100%);
        opacity: 0;
    }

    100% {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes notification-slide-out {
    0% {
        transform: translateX(0);
        opacity: 1;
    }

    100% {
        transform: translateX(100%);
        opacity: 0;
    }
}

.notification-container {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    pointer-events: none;
}

@media (max-width: 640px) {
    .notification-container {
        align-items: center;
    }
}
</style>

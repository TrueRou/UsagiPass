<script setup lang="ts">
import type { Notification } from '~/stores/notifications'

const { notifications, removeNotification } = useNotificationsStore()

function getAlertClass(type: Notification['type']) {
    const classes = {
        success: 'alert-success',
        error: 'alert-error',
        warning: 'alert-warning',
        info: 'alert-info',
    }
    return classes[type]
}
</script>

<template>
    <div class="toast toast-top toast-end z-50">
        <TransitionGroup name="notification" tag="div">
            <div
                v-for="notification in notifications" :key="notification.id" class="alert shadow-lg max-w-sm"
                :class="getAlertClass(notification.type)"
            >
                <svg
                    v-if="notification.type === 'success'" xmlns="http://www.w3.org/2000/svg"
                    class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                <svg
                    v-else-if="notification.type === 'error'" xmlns="http://www.w3.org/2000/svg"
                    class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                <svg
                    v-else-if="notification.type === 'warning'" xmlns="http://www.w3.org/2000/svg"
                    class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
                    />
                </svg>
                <svg
                    v-else xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                <span>{{ notification.message }}</span>
                <button class="btn btn-xs btn-ghost" @click="removeNotification(notification.id)">
                    ✕
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.notification-enter-active,
.notification-leave-active {
    transition: all 0.3s ease;
}

.notification-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.notification-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

.notification-move {
    transition: transform 0.3s ease;
}
</style>

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NotificationType = 'info' | 'success' | 'warning' | 'error'

export interface Notification {
    id: number
    type: NotificationType
    title: string
    message: string
    timeout?: number
    isPersistent?: boolean
}

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref<Notification[]>([])
    let nextId = 1

    function add(notification: Omit<Notification, 'id'>) {
        const id = nextId++
        const newNotification = {
            id,
            ...notification,
            timeout: notification.timeout || (notification.isPersistent ? 0 : 5000)
        }
        notifications.value.push(newNotification)

        // 如果不是持久通知，则设置自动移除
        if (!notification.isPersistent && notification.timeout !== 0) {
            setTimeout(() => {
                remove(id)
            }, notification.timeout || 5000)
        }

        return id
    }

    function remove(id: number) {
        const index = notifications.value.findIndex(n => n.id === id)
        if (index !== -1) {
            notifications.value.splice(index, 1)
        }
    }

    function info(title: string, message: string, options = {}) {
        return add({
            type: 'info',
            title,
            message,
            ...options
        })
    }

    function success(title: string, message: string, options = {}) {
        return add({
            type: 'success',
            title,
            message,
            ...options
        })
    }

    function warning(title: string, message: string, options = {}) {
        return add({
            type: 'warning',
            title,
            message,
            ...options
        })
    }

    function error(title: string, message: string, options = {}) {
        return add({
            type: 'error',
            title,
            message,
            ...options
        })
    }

    function clearAll() {
        notifications.value = []
    }

    return {
        notifications,
        add,
        remove,
        info,
        success,
        warning,
        error,
        clearAll
    }
})

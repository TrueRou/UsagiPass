export interface Notification {
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    duration?: number
}

export const useNotificationsStore = defineStore('notifications', () => {
    const notifications = ref<Notification[]>([])

    const removeNotification = (id: string) => {
        const index = notifications.value.findIndex(n => n.id === id)
        if (index > -1) {
            notifications.value.splice(index, 1)
        }
    }

    const addNotification = (notification: Omit<Notification, 'id'>) => {
        const id = Date.now().toString()
        const newNotification: Notification = {
            id,
            duration: 3000,
            ...notification,
        }

        notifications.value.push(newNotification)

        // 自动移除通知
        if (newNotification.duration && newNotification.duration > 0) {
            setTimeout(() => {
                removeNotification(id)
            }, newNotification.duration)
        }

        return id
    }

    const clearAll = () => {
        notifications.value = []
    }

    return {
        notifications: readonly(notifications),
        addNotification,
        removeNotification,
        clearAll,
    }
})

import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useServerStore } from '@/stores/server'
import DXPassView from '@/views/DXPassView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: DXPassView
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('../views/SettingsView.vue')
        }
    ]
})

router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const serverStore = useServerStore()

    if (to.query.maid) userStore.maimaiCode = to.query.maid as string
    if (to.query.time) userStore.timeLimit = to.query.time as string
    if (!serverStore.serverMessage) await serverStore.refreshMotd()
    if (localStorage.getItem('token')) await userStore.refreshUser()

    if (!userStore.isSignedIn && to.name !== 'login') {
        next({ name: 'login' })
    }
    else if (userStore.isSignedIn && to.name === 'login') {
        next({ name: 'home' })
    }

    else next()
})

export default router

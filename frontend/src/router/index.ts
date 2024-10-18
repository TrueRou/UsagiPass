import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useUserStore } from '@/stores/user'
import { useServerStore } from '@/stores/server'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
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
    await serverStore.refreshMotd()
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

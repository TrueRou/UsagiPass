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
            path: '/about',
            name: 'about',
            component: () => import('../views/AboutView.vue')
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
    await userStore.refreshUser()
    if (!userStore.isSignedIn) {
        // TODO: Redirect to the error page if the user is not signed in
    }
    next()
})

export default router

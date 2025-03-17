import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useServerStore } from '@/stores/server'
import DXPassView from '@/views/DXPassView.vue'
import DXCardView from '@/views/DXCardView.vue'
import { useImageStore } from '@/stores/image'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            meta: { requireAuth: true },
            component: DXPassView
        },
        {
            path: '/card/:uuid',
            name: 'card',
            props: true,
            component: DXCardView,
        },
        {
            path: '/cropper/:kind',
            name: 'cropper',
            props: true,
            meta: { requireAuth: true },
            component: () => import('../views/CropperView.vue'),
        },
        {
            path: '/',
            name: 'menus',
            component: () => import('../views/MenuView.vue'),
            children: [
                {
                    path: 'login',
                    name: 'login',
                    component: () => import('../components/menus/Login.vue')
                },
                {
                    path: 'preferences',
                    name: 'preferences',
                    meta: { requireAuth: true, requireImages: true },
                    component: () => import('../components/menus/Preferences.vue'),
                },
                {
                    path: 'update',
                    name: 'update',
                    meta: { requireAuth: true },
                    component: () => import('../components/menus/Update.vue')
                },
                {
                    path: 'bind/:server',
                    name: 'bind',
                    props: true,
                    meta: { requireAuth: true },
                    component: () => import('../components/menus/Bind.vue')
                },
                {
                    path: 'gallery/:kind',
                    name: 'gallery',
                    props: true,
                    meta: { requireImages: true },
                    component: () => import('../components/menus/Gallery.vue'),
                },
                {
                    path: 'designer/:uuid?',
                    name: 'designer',
                    props: true,
                    meta: { requireImages: true },
                    component: () => import('../components/menus/Designer.vue'),
                },
            ]
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        },
    ]
})

router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const imageStore = useImageStore();
    const serverStore = useServerStore()

    if (to.query.maid) userStore.maimaiCode = to.query.maid as string
    if (to.query.time) userStore.timeLimit = to.query.time as string
    if (!serverStore.serverMessage) await serverStore.refreshMotd()
    if (localStorage.getItem('token') && !userStore.userProfile) await userStore.refreshUser()
    if (to.meta.requireImages && !imageStore.images) imageStore.refreshImages().catch(() => { console.log('Failed to refresh images') })

    if (!userStore.isSignedIn && to.meta.requireAuth) next({ name: 'login' })
    else if (userStore.isSignedIn && to.name === 'login') next({ name: 'home' })
    else next()
})

export default router

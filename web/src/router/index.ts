import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import DXPassView from '@/views/DXPassView.vue'
import { useImageStore } from '@/stores/image'
import { useNotificationStore } from '@/stores/notification'
import { Privilege } from '@/types'

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
                    component: () => import('../components/menus/Login.vue'),
                },
                {
                    path: 'preferences/pass',
                    name: 'preferencesPass',
                    meta: { requireAuth: true, requireImages: true },
                    component: () => import('../components/menus/PreferencesPass.vue'),
                },
                {
                    path: 'update',
                    name: 'update',
                    meta: { requireAuth: true },
                    component: () => import('../components/menus/Update.vue'),
                },
                {
                    path: 'bind/:server',
                    name: 'bind',
                    props: true,
                    meta: { requireAuth: true },
                    component: () => import('../components/menus/Bind.vue'),
                },
                {
                    path: 'gallery/:kind',
                    name: 'gallery',
                    props: true,
                    meta: { requireImages: true },
                    component: () => import('../components/menus/Gallery.vue'),
                },
            ]
        },
        {
            path: '/admin',
            name: 'admin',
            meta: { requiresAuth: true, requiresAdmin: true },
            component: () => import('../views/AdminView.vue'),
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        },
    ]
})

router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const imageStore = useImageStore()
    const notificationStore = useNotificationStore()

    // Handle query parameters
    if (to.query.maid) userStore.maimaiCode = to.query.maid as string
    if (to.query.time) userStore.timeLimit = to.query.time as string

    // Load necessary data
    if (localStorage.getItem('token') && !userStore.userProfile) await userStore.refreshUser()
    if (to.meta.requireImages && !imageStore.images) await imageStore.refreshImages()

    // Check authentication first
    if (!userStore.isSignedIn) {
        // Handle routes requiring authentication
        if (to.meta.requireAuth || to.meta.requiresAdmin) {
            if (userStore.isSignedOut) {
                notificationStore.success("登出成功", "您已成功登出")
                userStore.isSignedOut = false;
            } else {
                notificationStore.warning("访问受限", "请先登录")
            }
            return next({ name: 'login' })
        }
    } else {
        // User is signed in
        if (to.name === 'login' && from.name !== 'login') {
            notificationStore.success("正在跳转", "您已登录, 即将回到上一页面")
            return next(from)
        }

        // Check admin access
        if (to.meta.requiresAdmin && userStore.userProfile?.privilege !== Privilege.ADMIN) {
            notificationStore.error("访问受限", "您没有管理员权限")
            return next({ name: 'home' })
        }
    }

    next()
})

export default router

export function useTour() {
    const router = useRouter()
    const { $leporid } = useNuxtApp()
    const nuxtApp = useNuxtApp()
    const { inTour } = storeToRefs(useContextStore())

    const tourUsername = 'Ｗａｒｍａ'
    const tourRating = 15000
    const tourFriendCode = '114514-1919810'

    /**
     * 启动主页引导（第一阶段）
     */
    function startMainPageTour() {
        const intro = nuxtApp.$intro.tour()
        inTour.value = true

        intro.setOptions({
            steps: [
                {
                    title: '欢迎使用 UsagiPass！',
                    intro: '让我们快速了解一下主要功能，帮助您更好地使用本项目。',
                },
                {
                    element: '[data-tour="dx-rating"]',
                    title: 'DX Rating 显示',
                    intro: '这里显示您的游戏评级（DX Rating）。您可以在设置中自定义显示的数值。',
                    position: 'right',
                },
                {
                    element: '[data-tour="player-info"]',
                    title: '玩家信息',
                    intro: '这里展示您的玩家名称和好友代码，可以在设置中进行修改。',
                    position: 'left',
                },
                {
                    element: '[data-tour="rocket-button"]',
                    title: '小火箭更新',
                    intro: '点击小火箭可以更新绑定账号的数据，包括上方的 Rating、玩家名称等信息。更新后会自动刷新显示。',
                    position: 'top',
                },
                {
                    element: '[data-tour="settings-button"]',
                    title: '个人设置',
                    intro: '点击此按钮可以进入设置页面，修改个人偏好、更换图片、管理账号等。接下来让我们进入设置页面看看吧！',
                    position: 'top',
                },
            ],
            nextLabel: '下一步',
            prevLabel: '上一步',
            doneLabel: '进入设置',
            skipLabel: '',
            showProgress: true,
            showBullets: false,
            exitOnOverlayClick: false,
            scrollToElement: true,
            scrollPadding: 30,
            disableInteraction: true,
        })

        intro.onComplete(async () => {
            // 跳转到设置页，并启动第二阶段引导
            await router.push('/preference?tour=continue')
            inTour.value = false
        })

        intro.onExit(async () => {
            // 用户跳过引导，更新 skipTour
            await updateSkipTour()
            inTour.value = false
        })

        intro.start()
    }

    /**
     * 启动设置页引导（第二阶段）
     */
    function startPreferenceTour() {
        const intro = nuxtApp.$intro.tour()

        intro.setOptions({
            steps: [
                {
                    title: '设置页面',
                    intro: '在这里您可以自定义各种显示选项和管理您的查分器账号。',
                },
                {
                    element: '[data-tour="image-settings"]',
                    title: '图片预览与设定',
                    intro: '独特的背景与立绘是 UsagiPass 的核心。点击图片可以更换角色、遮罩、背景和边框等素材，打造专属赛博 DX Pass。',
                    position: 'top',
                },
                {
                    element: '[data-tour="account-settings"]',
                    title: '账号绑定',
                    intro: '在这里添加和管理您的查分器账号。绑定账号后，点击主页的小火箭即可自动更新数据。',
                    position: 'top',
                },
                {
                    element: '[data-tour="add-account"]',
                    title: '新增账号',
                    intro: '点击此按钮可以添加新的查分器账号，支持多个查分器和 UsagiLab 通行证绑定。',
                    position: 'left',
                },
                {
                    element: '[data-tour="merge-account"]',
                    title: '合并账户',
                    intro: '如果您有多个 UsagiLab 通行证，可以在这里合并它们。您也可以随时从这里重新开始本引导。',
                    position: 'bottom',
                },
                {
                    element: '[data-tour="save-button"]',
                    title: '保存设置',
                    intro: '修改任何设置后，记得点击保存按钮来应用更改。现在您已经了解了所有主要功能，即刻开启您的 UsagiPass 之旅吧！',
                    position: 'top',
                },
            ],
            nextLabel: '下一步',
            prevLabel: '上一步',
            doneLabel: '完成',
            skipLabel: '',
            showProgress: true,
            showBullets: false,
            exitOnOverlayClick: false,
            scrollToElement: true,
            scrollPadding: 30,
            disableInteraction: true,
        })

        intro.onExit(async () => {
            await updateSkipTour()
            await router.replace('/preference')
        })

        intro.start()
    }

    /**
     * 更新用户的 skipTour 偏好
     */
    async function updateSkipTour() {
        await $leporid('/api/nuxt/profile/tour', { method: 'POST' })
    }

    /**
     * 手动重启引导（从主页开始）
     */
    async function restartTour() {
        // 导航到主页并启动引导
        await router.push('/')
        // 延迟启动引导，确保页面完全加载
        setTimeout(() => {
            startMainPageTour()
        }, 500)
    }

    return {
        startMainPageTour,
        startPreferenceTour,
        restartTour,
        inTour,
        tourUsername,
        tourRating,
        tourFriendCode,
    }
}

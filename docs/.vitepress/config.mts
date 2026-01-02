import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    lang: 'zh-CN',
    title: 'UsagiPass',
    description: 'UsagiPass 文档',
    themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: '主页', link: '/' },
            { text: '手册', link: '/implementation' },
            { text: '博客', link: 'https://turou.fun/' },
            { text: '❤️', link: 'https://afdian.com/a/turou' },
        ],

        sidebar: [
            {
                text: '介绍',
                items: [
                    { text: '安装', link: '/begin' },
                ],
            },
            {
                text: '代理',
                items: [
                    { text: 'Clash', link: '/proxies/clash' },
                    { text: 'Shadowrocket', link: '/proxies/rocket' },
                    { text: 'Sing-box', link: '/proxies/singbox' },
                    { text: 'Quantumult X', link: '/proxies/quantx' },
                ],
            },
            {
                text: '手册',
                items: [
                    { text: '实现方式', link: '/implementation' },
                    { text: '参与开发', link: '/development' },
                ],
            },
            {
                text: '其他',
                items: [
                    { text: '隐私政策', link: '/privacy-policy' },
                    { text: '服务条款', link: '/terms-of-use' },
                    { text: '特别感谢', link: '/thanks' },
                ],
            },
        ],

        footer: {
            message: '欢迎加入 UsagiPass 兔兔群：363346002',
            copyright: 'Copyright © 2019-2025 TuRou',
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/TrueRou/UsagiPass' },
        ],
    },
})

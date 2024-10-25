import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: 'zh-CN',
  title: "UsagiPass",
  titleTemplate: ':title - UsagiPass',
  description: "UsagiPass 文档",
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
        ]
      },
      {
        text: '代理',
        items: [
          { text: 'Clash', link: '/proxies/clash' },
          { text: 'Shadowrocket', link: '/proxies/rocket' },
          { text: 'Sing-box', link: '/proxies/singbox' },
        ]
      },
      {
        text: '手册',
        items: [
          { text: '实现方式', link: '/implementation' },
          { text: '参与开发', link: '/development' }
        ]
      }
    ],

    footer: {
      message: '欢迎加入UsagiPass兔兔群: 363346002',
      copyright: 'Copyright © 2019-2024 TuRou'
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/TrueRou/UsagiPass' }
    ]
  }
})

import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "UsagiPass",
  description: "UsagiPass 文档",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '主页', link: '/' },
      { text: '手册', link: '/implementation' }
    ],

    sidebar: [
      {
        text: '介绍',
        items: [
          { text: '安装', link: '/get-started' },
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

    socialLinks: [
      { icon: 'github', link: 'https://github.com/TrueRou/UsagiPass' }
    ]
  }
})

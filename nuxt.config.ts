// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: { enabled: process.env.NODE_ENV === 'development' },
    modules: ['@pinia/nuxt', '@nuxtjs/i18n', '@nuxt/eslint', 'nuxt-auth-utils'],
    css: ['~/assets/css/main.css'],
    app: {
        head: {
            link: [
                { rel: 'dns-prefetch', href: 'https://eo.assets.turou.fun' },
                { rel: 'preconnect', href: 'https://eo.assets.turou.fun', crossorigin: '' },
            ],
        },
    },
    vite: {
        plugins: [
            tailwindcss(),
        ],
        build: {
            sourcemap: false,
        },
        optimizeDeps: {
            include: [
                '@intlify/core',
                '@intlify/core-base',
                '@intlify/message-compiler',
                '@intlify/shared',
                '@intlify/utils/h3',
                '@vue/devtools-core',
                '@vue/devtools-kit',
                'intro.js',
                'qrcode', // CJS
                'ufo',
                'vue-cropper',
                'vue-i18n',
            ],
        },
    },
    eslint: {
        config: {
            standalone: false, // <---
        },
    },
    runtimeConfig: {
        session: {
            name: 'nuxt-session',
            password: process.env.NUXT_SESSION_PASSWORD || '',
            maxAge: 31536000,
            cookie: {
                sameSite: 'lax',
            },
        },
        usagipass: {
            databaseURL: 'postgresql://postgres:password@localhost:5432/usagipass',
        },
        mitmproxy: {
            enabled: true,
            listenHost: '127.0.0.1',
            listenPort: 7300,
        },
        // UsagiLab 账号登录（OAuth 授权码 + PKCE），凭据通过 NUXT_OAUTH_OIDC_* 注入
        oauth: {
            oidc: {
                clientId: '',
                clientSecret: '',
            },
        },
        leporidae: {
            baseURL: 'https://api.turou.fun/leporidae',
            fePublicURL: 'https://hoshirabi.com',
            developerToken: '4616dd015b6139704d259ea9c1a0e29d',
            defaultImage: {
                characterId: '2e7046aa-ddc2-40fb-bf5d-5236ffca50f9',
                maskId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                backgroundId: '6a742fd3-f9e2-4edf-ab65-9208fae30d36',
                frameId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                passnameId: 'f6988add-bb65-4b78-a69c-7d01c453d4a8',
            },
        },
        public: {
            URL: 'https://up.turou.fun',
            imageURL: 'https://eo.assets.turou.fun/leporidae/images',
            imagePreviewURL: 'https://eo.assets.turou.fun/leporidae/thumbnails',
        },
    },
    i18n: {
        defaultLocale: 'zh-CN',
        strategy: 'no_prefix',
        locales: [
            {
                code: 'zh-CN',
                flag: 'CN',
                name: '简体中文 (中国)',
            },
        ],
    },
    // nuxt-auth-utils 依赖 @nuxt/schema 4.6.1，在 shamefully-hoist 下盖过了 nuxt 自带的 4.4.8，
    // 使 nitro 配置类型退化为只含少数字段的回退类型；对齐 @nuxt/schema 版本后可移除此断言
    nitro: {
        preset: 'bun',
    } as Record<string, any>,
})

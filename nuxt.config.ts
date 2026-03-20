// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: { enabled: true },
    modules: ['@pinia/nuxt', '@nuxtjs/i18n', '@nuxt/eslint', 'nuxt-auth-utils'],
    css: ['~/assets/css/main.css', 'intro.js/introjs.css'],
    vite: {
        plugins: [
            tailwindcss(),
        ],
        build: {
            sourcemap: false,
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
            URL: 'http://localhost:7200',
            databaseURL: 'postgresql://postgres:password@localhost:5432/usagipass',
        },
        mitmproxy: {
            enabled: true,
            listenHost: '127.0.0.1',
            listenPort: 7300,
        },
        leporid: {
            baseURL: 'https://api.dev.turou.fun/leporid',
            defaultImage: {
                characterId: '2e7046aa-ddc2-40fb-bf5d-5236ffca50f9',
                maskId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                backgroundId: '6a742fd3-f9e2-4edf-ab65-9208fae30d36',
                frameId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                passnameId: 'f6988add-bb65-4b78-a69c-7d01c453d4a8',
            },
        },
        otoge: {
            baseURL: 'https://api.dev.turou.fun/otoge',
            developerToken: 'de5ca192916344b360f391d83e20ba85',
        },
        public: {
            imageURL: 'https://assets.dev.turou.fun/leporid/images',
            imagePreviewURL: 'https://assets.dev.turou.fun/leporid/thumbnails',
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
    nitro: {
        preset: 'bun',
    },
})

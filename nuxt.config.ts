// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: { enabled: true },
    modules: ['@pinia/nuxt', '@nuxtjs/i18n', '@nuxt/eslint'],
    css: ['~/assets/css/main.css'],
    vite: {
        plugins: [
            tailwindcss(),
        ],
    },
    i18n: {
        defaultLocale: 'zh-CN',
        strategy: 'no_prefix',
        locales: [
            {
                code: 'en-GB',
                flag: 'GB',
                name: 'English (International)',
                file: 'en-GB.json',
            },
            {
                code: 'zh-CN',
                flag: 'CN',
                name: '简体中文 (中国)',
                file: 'zh-CN.json',
            },
        ],
    },
    eslint: {
        config: {
            standalone: false, // <---
        },
    },
    runtimeConfig: {
        usagipass: {
            baseURL: 'http://localhost:6000',
            databaseURL: 'postgresql://postgres:password@localhost:5432/usagipass',
        },
        mitmproxy: {
            enabled: true,
            listenHost: '127.0.0.1',
            listenPort: 6100,
        },
        leporid: {
            baseURL: 'http://43.139.192.17:3000',
            cookieName: 'lep_session',
            defaultImage: {
                characterId: '2e7046aa-ddc2-40fb-bf5d-5236ffca50f9',
                maskId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                backgroundId: '6a742fd3-f9e2-4edf-ab65-9208fae30d36',
                frameId: '421943e9-2221-45f1-8f76-5a1ca012028e',
                passnameId: 'f6988add-bb65-4b78-a69c-7d01c453d4a8',
            },
        },
        otoge: {
            baseURL: 'http://43.139.192.17:3000',
        },
        public: {
            imageURL: 'https://uc.turou.fun/api/images',
            imagePreviewURL: 'https://uc.turou.fun/api/images',
        },
    },
})

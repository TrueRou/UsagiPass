export default defineNuxtPlugin(() => {
    let introPromise: Promise<typeof import('intro.js').default> | null = null

    async function getIntro() {
        if (!introPromise) {
            await import('intro.js/introjs.css')
            introPromise = import('intro.js').then(mod => mod.default)
        }
        return introPromise
    }

    return {
        provide: {
            getIntro,
        },
    }
})

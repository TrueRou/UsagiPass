import introJs from 'intro.js'

export default defineNuxtPlugin(() => {
    return {
        provide: {
            intro: introJs,
        },
    }
})

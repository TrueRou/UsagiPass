export const useContextStore = defineStore('context', () => {
    const dateLimit = ref<string | undefined>(undefined)
    const timeLimit = ref<string | undefined>(undefined)
    const maimaiMaid = ref<string | undefined>(undefined)

    return {
        dateLimit,
        timeLimit,
        maimaiMaid,
    }
})

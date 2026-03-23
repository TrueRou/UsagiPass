<script setup lang="ts">
const props = defineProps<{
    rating?: string
}>()

const ratingLevels: any = [
    1000,
    2000,
    4000,
    7000,
    10000,
    12000,
    13000,
    14000,
    14500,
    15000,
]

const canvasRef = ref<HTMLCanvasElement | null>(null)

const getNum = async (id: string) => (await import(`../../assets/icons/rating/num/UI_CMN_Num_26p_${id}.png`)).default
const getBase = async (id: string) => (await import(`../../assets/icons/rating/UI_CMA_Rating_Base_${id}.png`)).default

function countOccurrences(str: string, searchTerm: string) {
    let count = 0
    let index = str.indexOf(searchTerm)
    while (index !== -1) {
        count++
        index = str.indexOf(searchTerm, index + searchTerm.length)
    }
    return count
}

const numImageIds = computed(() => {
    const numValue = props.rating?.replace(/\+/g, '').replace(/-/g, '')
    if (!numValue || Number.isNaN(Number(numValue)))
        return []
    const arr = numValue.split('')
    while (arr.length < 5) arr.unshift('10')
    return arr.slice(0, 5)
})

const baseImageId = computed(() => {
    const numValue = props.rating?.replace(/\+/g, '').replace(/-/g, '')
    if (!numValue || Number.isNaN(Number(numValue)))
        return '0'
    let rating = Number.parseInt(numValue)
    rating = Math.max(ratingLevels[0], Math.min(rating, ratingLevels[9]))
    let stage = 0
    while (rating >= ratingLevels[stage + 1]) stage++

    const sideEffect = countOccurrences(props.rating || '', '+') - countOccurrences(props.rating || '', '-')
    const finalValue = Math.max(Math.min(stage + 1 + sideEffect, 10), 0)

    return String(finalValue)
})

async function drawCanvas() {
    const scale = 0.8
    const canvas = canvasRef.value
    if (!canvas)
        return

    const ctx = canvas.getContext('2d')
    if (!ctx)
        return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const [baseSrc, numSrcs] = await Promise.all([
        getBase(baseImageId.value),
        Promise.all(numImageIds.value.map(id => getNum(id))),
    ])

    const baseImg = new Image()
    baseImg.fetchPriority = 'high'
    baseImg.src = baseSrc

    baseImg.onload = () => {
        ctx.drawImage(baseImg, 0, 0, canvas.width, canvas.height)

        const numImgPromises = numSrcs.map((src) => {
            const img = new Image()
            img.fetchPriority = 'high'
            img.src = src
            return new Promise<HTMLImageElement>((resolve) => {
                img.onload = () => resolve(img)
                img.onerror = () => resolve(img)
            })
        })

        Promise.all(numImgPromises).then((numImgs) => {
            numImgs.forEach((img, index) => {
                if (img.complete && img.naturalHeight !== 0) {
                    ctx.drawImage(img, 115 + index * 28, 20, 34 * scale, 40 * scale)
                }
            })
        })
    }
}

onMounted(drawCanvas)
watch([() => props.rating, baseImageId, numImageIds], drawCanvas)
</script>

<template>
    <canvas
        ref="canvasRef" width="269" height="70" class="ms-auto"
        :class="{ invisible: props.rating === undefined || isNaN(parseInt(props.rating)) }"
    />
</template>

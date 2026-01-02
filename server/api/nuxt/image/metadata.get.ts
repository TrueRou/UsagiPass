async function getMaimaiMetadata(characterId: number): Promise<MaimaiCharacter | null> {
    const response = await $fetch<{
        code: number
        message: string
        data: MaimaiCharacter[]
    }>(`/api/otoge/maimai/characters?id=${characterId}`, { method: 'GET' })
    return response.data.length > 0 ? response.data[0] ?? null : null
}

async function getChunithmMetadata(cardId: number): Promise<ChunithmCharacter | null> {
    const response = await $fetch<{
        code: number
        message: string
        data: ChunithmCharacter[]
    }>(`/api/otoge/chunithm/characters?id=${cardId}`, { method: 'GET' })
    return response.data.length > 0 ? response.data[0] ?? null : null
}

async function getOngekiMetadata(cardId: number): Promise<OngekiCard | null> {
    const response = await $fetch<{
        code: number
        message: string
        data: OngekiCard[]
    }>(`/api/otoge/ongeki/cards?id=${cardId}`, { method: 'GET' })
    return response.data.length > 0 ? response.data[0] ?? null : null
}

export default defineEventHandler(async (event) => {
    const imageId = getQuery(event).id as string | undefined

    if (!imageId) {
        return {
            code: 500,
            message: '缺少图片 ID 参数',
            data: null,
        }
    }

    const imageResponse = await $fetch<{
        code: number
        message: string
        data?: ImageResponse
    }>(`/api/images/${imageId}`, {
        method: 'GET',
        ignoreResponseError: true,
    })

    if (imageResponse.code !== 200 || !imageResponse.data) {
        return {
            code: 500,
            message: '获取图片信息请求失败',
            data: null,
        }
    }

    const metadataId = imageResponse.data.original_id
    let maskImage: ImageResponse | null = null
    let source: string | null = null
    let characterName: string | null = null
    let version: string | null = null

    if (metadataId) {
        const imageListResponse = await $fetch<{
            code: number
            message: string
            data?: { images: { records: ImageResponse[] } }
        }>(`/api/images`, {
            method: 'GET',
            ignoreResponseError: true,
            query: {
                original_id: metadataId,
            },
        })

        if (imageListResponse.code === 200 && imageListResponse.data) {
            maskImage = imageListResponse.data.images.records.find(
                img => img.labels.includes('mask'),
            ) ?? null
        }

        if (metadataId.startsWith('chu_')) {
            const result = await getChunithmMetadata(Number(metadataId.slice(4)))
            if (result) {
                source = 'CHUNITHM'
                characterName = result.name
                if (characterName.includes('【')) {
                    characterName = characterName.split('【')[0] as string
                }
                if (characterName.includes('／')) {
                    characterName = characterName.split('／')[0] as string
                }
            }
        }
        else if (metadataId.startsWith('mai_')) {
            const result = await getMaimaiMetadata(Number(metadataId.slice(4)))
            if (result) {
                source = 'maimai でらっくす'
                characterName = result.name
                version = `[maimaiDX]${result.version}`
            }
        }
        else if (metadataId.startsWith('mu3_')) {
            const result = await getOngekiMetadata(Number(metadataId.slice(4)))
            if (result) {
                source = 'オンゲキ'
                characterName = result.character_name
                version = `[O.N.G.E.K.I.]${result.version_number}`
            }
        }
    }

    return {
        code: 200,
        message: '请求成功',
        data: {
            source,
            version,
            character_name: characterName,
            mask_image: maskImage,
        },
    }
})

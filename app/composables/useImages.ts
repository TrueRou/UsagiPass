interface UseImagesOptions {
    aspectId: string
    pageSize?: number
    initialFilters?: string[] | null
}

interface ListOptions {
    pageNumber?: number
    filters?: string[] | null
    pageSize?: number
    keyword?: string
}

interface UploadResult {
    image: ImageResponse
}

function unwrapPayload<T>(payload: T | { data: T }): T {
    if (payload && typeof payload === 'object' && 'data' in (payload as Record<string, unknown>)) {
        return (payload as { data: T }).data
    }
    return payload as T
}

export function useImages(options: UseImagesOptions) {
    const { $leporid } = useNuxtApp()

    const aspect = shallowRef<ImageAspect | null>(null)
    const images = ref<ImageResponse[]>([])
    const loading = ref(false)
    const error = ref<Error | null>(null)
    const pageNumber = ref(1)
    const pageSize = ref(options.pageSize ?? 20)
    const totalPage = ref(0)
    const totalRow = ref(0)
    const activeFilters = ref<string[] | null>(options.initialFilters ?? null)
    const availableLabels = ref<string[]>([])
    const currentAspectId = ref(options.aspectId)

    const fetchAspect = async () => {
        loading.value = true
        try {
            if (aspect.value && aspect.value.id === currentAspectId.value) {
                return aspect.value
            }
            const response = await $leporid<ImageAspect | { data: ImageAspect }>(`/api/images/aspects/${currentAspectId.value}`, {
                method: 'GET',
            })
            aspect.value = unwrapPayload<ImageAspect>(response)
            return aspect.value
        }
        finally {
            loading.value = false
        }
    }

    const list = async (listOptions: ListOptions = {}) => {
        loading.value = true
        error.value = null
        try {
            if (listOptions.pageNumber !== undefined) {
                pageNumber.value = listOptions.pageNumber
            }
            if (listOptions.pageSize !== undefined) {
                pageSize.value = listOptions.pageSize
            }
            if (listOptions.filters !== undefined) {
                activeFilters.value = [...listOptions.filters ?? [], ...options.initialFilters ?? []]
            }

            const query: Record<string, any> = {
                aspect_id: currentAspectId.value,
                page_number: pageNumber.value,
                page_size: pageSize.value,
                labels: Array.from(new Set(activeFilters.value ?? [])),
            }

            if (listOptions.keyword) {
                query.keyword = listOptions.keyword
            }

            const response = await $leporid<ImageSearchResponse | { data: ImageSearchResponse }>('/api/images', {
                method: 'GET',
                query,
            })
            const payload = unwrapPayload<ImageSearchResponse>(response)
            images.value = payload.images.records ?? []
            pageNumber.value = payload.images.page_number ?? pageNumber.value
            pageSize.value = payload.images.page_size ?? pageSize.value
            totalPage.value = payload.images.total_page ?? 0
            totalRow.value = payload.images.total_row ?? 0
            availableLabels.value = payload.labels ?? []

            return {
                images: images.value,
                total: totalRow.value,
            }
        }
        catch (err) {
            error.value = err as Error
            throw err
        }
        finally {
            loading.value = false
        }
    }

    const refresh = async () => {
        return list()
    }

    const updateImage = async (uuid: string, payload: ImageUpdateRequest) => {
        await $leporid(`/api/images/${uuid}`, {
            method: 'PUT',
            body: payload,
        })
        await refresh()
    }

    const deleteImage = async (uuid: string) => {
        await $leporid(`/api/images/${uuid}`, {
            method: 'DELETE',
        })
        // 如果当前页删除了最后一张图片且不是第一页，则回退一页以保证列表不空
        if (images.value.length <= 1 && pageNumber.value > 1) {
            pageNumber.value -= 1
        }
        await refresh()
    }

    const uploadImage = async (formData: FormData): Promise<UploadResult> => {
        const response = await $leporid<ImageResponse | { data: ImageResponse }>('/api/images', {
            method: 'POST',
            body: formData,
        })
        const created = unwrapPayload<ImageResponse>(response)
        await refresh()
        return { image: created }
    }

    const customImages = computed(() => images.value.filter(image => image.visibility === 'PRIVATE'))

    const setAspectId = (aspectId: string) => {
        if (currentAspectId.value !== aspectId) {
            currentAspectId.value = aspectId
            aspect.value = null
            activeFilters.value = options.initialFilters ?? null
        }
    }

    const representativeLabels = computed(() => {
        const allLabels = [...availableLabels.value, ...activeFilters.value ?? []]
        const filteredLabels = allLabels.filter(label => !options.initialFilters?.includes(label))
        return Array.from(new Set(filteredLabels))
    })

    return {
        aspect,
        fetchAspect,
        images,
        loading,
        error,
        pageNumber,
        pageSize,
        totalRow,
        totalPage,
        activeFilters,
        list,
        refresh,
        updateImage,
        deleteImage,
        uploadImage,
        availableLabels,
        representativeLabels,
        customImages,
        setAspectId,
    }
}

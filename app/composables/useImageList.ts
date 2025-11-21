interface UseImageListOptions {
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

export function useImageList(options: UseImageListOptions) {
    const { $leporid } = useNuxtApp()

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

            const response = await $leporid<ImageSearchResponse>('/api/images', {
                method: 'GET',
                query,
            })
            images.value = response.images.records ?? []
            pageNumber.value = response.images.page_number ?? pageNumber.value
            pageSize.value = response.images.page_size ?? pageSize.value
            totalPage.value = response.images.total_page ?? 0
            totalRow.value = response.images.total_row ?? 0
            availableLabels.value = response.labels ?? []

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

    const customImages = computed(() => images.value.filter(image => image.visibility === 'PRIVATE'))

    const representativeLabels = computed(() => {
        const allLabels = [...availableLabels.value, ...activeFilters.value ?? []]
        const filteredLabels = allLabels.filter(label => !options.initialFilters?.includes(label))
        return Array.from(new Set(filteredLabels))
    })

    return {
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
        availableLabels,
        representativeLabels,
        customImages,
    }
}

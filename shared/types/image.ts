/**
 * 图片可见性枚举
 */
export enum ImageVisibility {
    DELETED = -1,
    PRIVATE = 0,
    PUBLIC = 1,
}

/**
 * 图片完整响应
 */
export interface ImageResponse {
    id: string
    name: string
    description: string
    visibility: ImageVisibility
    labels: string[]
    original_id?: string
    original_name?: string
    user_id: string
    aspect_id: string
}

/**
 * 图片简略响应
 */
export interface ImageSimpleResponse {
    id: string
    name: string
    description: string
    labels: string[]
}

/**
 * 图片搜索响应
 */
export interface ImageSearchResponse {
    labels: string[]
    images: {
        page_number: number
        page_size: number
        total_page: number
        total_row: number
        records: ImageSimpleResponse[]
    }
}

/**
 * 图片比例预设
 */
export interface ImageAspect {
    id: string
    name: string
    description?: string
    ratio_width_unit: number
    ratio_height_unit: number
}

/**
 * 图片上传请求
 */
export interface ImageUploadRequest {
    file: File
    name: string
    description: string
    visibility: ImageVisibility
    labels: string[]
    aspect_id: string
}

/**
 * 图片更新请求
 */
export interface ImageUpdateRequest {
    name: string
    description?: string
    visibility: ImageVisibility
    labels: string[]
}

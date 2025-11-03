/**
 * 图片可见性枚举
 */
export enum ImageVisibility {
    DELETED = 'DELETED',
    PRIVATE = 'PRIVATE',
    PUBLIC = 'PUBLIC',
}

/**
 * 图片响应
 */
export interface ImageResponse {
    user_id: string
    file_name: string
    metadata_id: string
    created_at: string
    updated_at: string
    id: string
    name: string
    description?: string
    visibility: ImageVisibility
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
        total: number
        records: ImageResponse[]
    }
}

/**
 * 图片比例预设
 */
export interface ImageAspect {
    id: string
    name: string
    description?: string
    ratioWidthUnit: number
    ratioHeightUnit: number
}

/**
 * 图片上传请求
 */
export interface ImageUploadRequest {
    file: File
    aspect_id: string
    name: string
    description?: string
    visibility: ImageVisibility
    labels: string[]
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

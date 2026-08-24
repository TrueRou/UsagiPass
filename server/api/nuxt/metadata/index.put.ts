import { z } from 'zod'

const metadataSchema = z.object({
    key: z.string().min(1).max(255),
    value: z.string(),
})

export default defineEventHandler(async (event) => {
    const session = await requireUserSession(event)

    if (!session.user.permissions.includes(UserPermission.METADATA_ADMIN)) {
        setResponseStatus(event, 403)
        return {
            code: 403,
            message: '没有修改 metadata 的权限',
            data: null,
        }
    }

    const result = metadataSchema.safeParse(await readBody(event))
    if (!result.success) {
        setResponseStatus(event, 400)
        return {
            code: 400,
            message: 'metadata 参数无效',
            data: null,
        }
    }

    const [metadata] = await useDrizzle().insert(tables.metadata).values({
        key: result.data.key,
        value: result.data.value,
        updatedBy: session.user.id,
    }).onConflictDoUpdate({
        target: tables.metadata.key,
        set: {
            value: result.data.value,
            updatedAt: new Date(),
            updatedBy: session.user.id,
        },
    }).returning()

    return {
        code: 200,
        message: 'metadata 已保存',
        data: metadata,
    }
})

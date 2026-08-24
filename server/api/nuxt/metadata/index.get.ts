export default defineEventHandler(async (event) => {
    const key = getQuery(event).key

    if (typeof key !== 'string' || !key) {
        setResponseStatus(event, 400)
        return {
            code: 400,
            message: '必须指定 metadata key',
            data: null,
        }
    }

    const metadata = await useDrizzle().query.metadata.findFirst({
        where: eq(tables.metadata.key, key),
    })

    return {
        code: 200,
        message: '请求成功',
        data: metadata || null,
    }
})

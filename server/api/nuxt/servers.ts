export default defineEventHandler(async (_) => {
    return {
        code: 200,
        message: '请求成功',
        data: await useDrizzle().query.server.findMany(),
    }
})

export default defineEventHandler(async (event) => {
    const session = await requireUserSession(event)
    const db = useDrizzle()

    await db.update(tables.userPreference)
        .set({ skipTour: true })
        .where(eq(tables.userPreference.userId, session.user.id))

    return {
        code: 200,
        message: '请求成功',
        data: null,
    }
})

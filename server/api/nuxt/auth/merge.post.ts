export default defineEventHandler(async (event) => {
    let { source, target } = await readBody(event)
    const db = useDrizzle()

    const user = await requireUserSession(event)

    source = source ?? user.secure!.accessToken
    target = target ?? user.secure!.accessToken

    let sourceUserId: string
    let targetUserId: string

    try {
        // 获取两个账户的信息
        const sourceUserResponse = await $fetch<{ data: UserResponse }>(`/api/users/me`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${source}`,
            },
        })

        const targetUserResponse = await $fetch<{ data: UserResponse }>(`/api/users/me`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${target}`,
            },
        })

        sourceUserId = sourceUserResponse.data.id
        targetUserId = targetUserResponse.data.id

        // 执行上游的合并任务
        await $fetch<null>(`/api/auth/merge`, {
            method: 'POST',
            body: {
                source_access_token: source,
                target_access_token: target,
            },
        })
    }
    catch (error: any) {
        return {
            code: error.statusCode || 500,
            message: error.data.message ?? '未知错误',
            data: null,
        }
    }

    // 执行 Nuxt 侧的合并任务
    db.transaction(async (tx) => {
        try {
            // 如果 sourceUserId 有用户偏好设置，则覆盖 targetUserId 的用户偏好设置
            const sourcePreference = await tx.query.userPreference.findFirst({
                where: eq(tables.userPreference.userId, sourceUserId),
            })
            if (sourcePreference) {
                await tx.delete(tables.userPreference).where(eq(tables.userPreference.userId, targetUserId))
                await tx.update(tables.userPreference)
                    .set({ userId: targetUserId })
                    .where(eq(tables.userPreference.userId, sourceUserId))
            }

            // 如果 sourceUserId 有用户评分，则覆盖 targetUserId 的用户评分
            const sourceRating = await tx.query.userRating.findFirst({
                where: eq(tables.userRating.userId, sourceUserId),
            })
            if (sourceRating) {
                await tx.delete(tables.userRating).where(eq(tables.userRating.userId, targetUserId))
                await tx.update(tables.userRating)
                    .set({ userId: targetUserId })
                    .where(eq(tables.userRating.userId, sourceUserId))
            }

            // 如果 sourceUserId 有绑定任何账户，则迁移所有到账户到 targetUserId
            const sourceAccount = await tx.query.userAccount.findFirst({
                where: eq(tables.userAccount.userId, sourceUserId),
            })
            if (sourceAccount) {
                await tx.delete(tables.userAccount).where(eq(tables.userAccount.userId, targetUserId))
                await tx.update(tables.userAccount)
                    .set({ userId: targetUserId })
                    .where(eq(tables.userAccount.userId, sourceUserId))
            }
        }
        catch (error) {
            tx.rollback()
            throw error
        }
    })

    return {
        code: 200,
        message: '账户合并成功',
        data: null,
    }
})

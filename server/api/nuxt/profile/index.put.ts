export default defineEventHandler(async (event) => {
    try {
        const userId = (await useUser(event)).id
        const db = useDrizzle()
        const body = await readBody<UserProfile>(event)

        // 更新用户偏好设置
        if (body.preference) {
            await db.insert(tables.userPreference).values({
                ...body.preference,
                userId,
            }).onConflictDoUpdate({
                target: tables.userPreference.userId,
                set: {
                    ...body.preference,
                },
            })
        }

        if (body.accounts) {
            const existingAccounts = await db.query.userAccount.findMany({
                where: eq(tables.userAccount.userId, userId),
            })
            const existingMap = new Map(existingAccounts.map(account => [account.id, account]))
            const incomingIds = new Set<number>()

            for (const account of body.accounts) {
                if (account.id != null) {
                    incomingIds.add(account.id)
                }

                const existingAccount = account.id != null ? existingMap.get(account.id) : undefined
                if (existingAccount) {
                    await db.update(tables.userAccount)
                        .set({ ...account, updatedAt: new Date() })
                        .where(eq(tables.userAccount.id, existingAccount.id))
                }
                else {
                    await db.insert(tables.userAccount).values({
                        ...account,
                        userId,
                    })
                }
            }

            for (const account of existingAccounts) {
                if (account.id != null && !incomingIds.has(account.id)) {
                    await db.delete(tables.userAccount)
                        .where(eq(tables.userAccount.id, account.id))
                }
            }
        }

        // 查询更新后的用户偏好设置
        const preference = await db.query.userPreference.findFirst({
            where: eq(tables.userPreference.userId, userId),
        })

        // 查询用户账号列表
        const userAccounts = await db.query.userAccount.findMany({
            where: eq(tables.userAccount.userId, userId),
        })

        // 查询用户评分信息
        const userRating = await db.query.userRating.findFirst({
            where: eq(tables.userRating.userId, userId),
        })

        const profile: UserProfile = {
            preference: preference!,
            accounts: userAccounts,
            player: userRating || null,
        }

        return {
            code: 200,
            message: '请求成功',
            data: profile,
        }
    }
    catch (error: any) {
        return {
            code: error.statusCode || 500,
            message: error instanceof Error ? error.message : '未知错误',
            data: null,
        }
    }
})

export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)

    // Guest: reject with helpful message
    if (!session?.user) {
        setResponseStatus(event, 401)
        return {
            code: 401,
            message: '访客模式无法保存设置，请先登录',
            data: null,
        }
    }

    const body = await readBody<UserProfile>(event)
    const db = useDrizzle()

    // 更新用户偏好设置
    if (body.preference) {
        // 剥离客户端传入的 userId：它是主键，且会出现在 ON CONFLICT DO UPDATE SET 中，
        // 一旦客户端传空串（游客默认值）就会触发 uuid 格式错误，传其他 uuid 则等于改写主键
        const { userId: _userId, ...preferenceFields } = body.preference

        await db.insert(tables.userPreference).values({
            ...preferenceFields,
            userId: session.user.id,
        }).onConflictDoUpdate({
            target: tables.userPreference.userId,
            set: {
                ...preferenceFields,
                // 显式回填服务端 userId：既不信任客户端，也保证 set 子句非空（空 set 是非法 SQL）
                userId: session.user.id,
            },
        })
    }

    if (body.accounts) {
        const existingAccounts = await db.query.userAccount.findMany({
            where: eq(tables.userAccount.userId, session.user.id),
        })
        const existingMap = new Map(existingAccounts.map(account => [account.id, account]))
        const incomingIds = new Set<string>()

        for (const account of body.accounts) {
            if (account.id != null) {
                incomingIds.add(account.id)
            }

            // 同样剥离客户端传入的 userId，避免账号归属被改写
            const { userId: _accountUserId, ...accountFields } = account

            const existingAccount = account.id != null ? existingMap.get(account.id) : undefined
            if (existingAccount) {
                await db.update(tables.userAccount)
                    .set({ ...accountFields, createdAt: new Date(account.createdAt), updatedAt: new Date() })
                    .where(eq(tables.userAccount.id, existingAccount.id))
            }
            else {
                await db.insert(tables.userAccount).values({
                    ...accountFields,
                    userId: session.user.id,
                    updatedAt: new Date(),
                    createdAt: new Date(),
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
        where: eq(tables.userPreference.userId, session.user.id),
    })

    // 查询用户账号列表
    const userAccounts = await db.query.userAccount.findMany({
        where: eq(tables.userAccount.userId, session.user.id),
    })

    // 查询用户评分信息
    const userRating = await db.query.userRating.findFirst({
        where: eq(tables.userRating.userId, session.user.id),
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
})

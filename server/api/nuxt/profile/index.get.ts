export default defineEventHandler(async (event) => {
    const userId = (await useUser(event)).id
    const db = useDrizzle()
    const config = useRuntimeConfig()

    // 查询用户偏好设置
    const preference = await db.query.userPreference.findFirst({
        where: eq(tables.userPreference.userId, userId),
    })

    // 如果用户偏好设置不存在，创建默认的偏好设置
    let userPreference = preference
    if (!userPreference) {
        const [newPreference] = await db.insert(tables.userPreference).values({
            userId,
            characterId: config.leporid.defaultImage.characterId,
            maskId: config.leporid.defaultImage.maskId,
            backgroundId: config.leporid.defaultImage.backgroundId,
            frameId: config.leporid.defaultImage.frameId,
            passnameId: config.leporid.defaultImage.passnameId,
        }).returning()
        userPreference = newPreference
    }

    // 查询用户账号列表
    const userAccounts = await db.query.userAccount.findMany({
        where: eq(tables.userAccount.userId, userId),
    })

    // 查询用户评分信息
    const userRating = await db.query.userRating.findFirst({
        where: eq(tables.userRating.userId, userId),
    })

    const profile: UserProfile = {
        preference: userPreference,
        accounts: userAccounts,
        player: userRating || null,
    }

    return {
        code: 200,
        message: '请求成功',
        data: profile,
    }
})

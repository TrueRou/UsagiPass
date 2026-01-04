export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const db = useDrizzle()
    const config = useRuntimeConfig()

    // Guest: return default profile
    if (!session?.user) {
        const defaultProfile: UserProfile = {
            preference: {
                userId: '',
                maimaiVersion: '',
                simplifiedCode: '',
                characterName: '',
                friendCode: '',
                displayName: '',
                dxRating: '',
                qrSize: 15,
                maskType: 0,
                playerInfoColor: '#ffffff',
                charaInfoColor: '#fee37c',
                showDxRating: true,
                showDisplayName: true,
                showFriendCode: true,
                showDate: true,
                enableMask: false,
                characterId: config.leporid.defaultImage.characterId,
                maskId: config.leporid.defaultImage.maskId,
                backgroundId: config.leporid.defaultImage.backgroundId,
                frameId: config.leporid.defaultImage.frameId,
                passnameId: config.leporid.defaultImage.passnameId,
                skipTour: false,
            },
            accounts: [],
            player: null,
        }
        return {
            code: 200,
            message: '请求成功',
            data: defaultProfile,
        }
    }

    // 查询用户偏好设置
    const preference = await db.query.userPreference.findFirst({
        where: eq(tables.userPreference.userId, session.user.id),
    })

    // 如果用户偏好设置不存在，创建默认的偏好设置
    let userPreference = preference
    if (!userPreference) {
        const [newPreference] = await db.insert(tables.userPreference).values({
            userId: session.user.id,
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
        where: eq(tables.userAccount.userId, session.user.id),
    })

    // 查询用户评分信息
    const userRating = await db.query.userRating.findFirst({
        where: eq(tables.userRating.userId, session.user.id),
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

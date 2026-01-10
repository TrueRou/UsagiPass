const DEFAULT_GUEST_PROFILE: UserPreference = {
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
    characterId: '2e7046aa-ddc2-40fb-bf5d-5236ffca50f9',
    maskId: '421943e9-2221-45f1-8f76-5a1ca012028e',
    backgroundId: '6a742fd3-f9e2-4edf-ab65-9208fae30d36',
    frameId: '421943e9-2221-45f1-8f76-5a1ca012028e',
    passnameId: 'f6988add-bb65-4b78-a69c-7d01c453d4a8',
    skipTour: false,
}

export default defineEventHandler(async (event) => {
    const isGuest = getCookie(event, 'guest')
    if (isGuest === 'true') {
        const guestPreferenceRaw = getCookie(event, 'guest_preference') as string | undefined
        const guestPreference = guestPreferenceRaw ? JSON.parse(guestPreferenceRaw) : DEFAULT_GUEST_PROFILE
        return {
            code: 200,
            message: '请求成功',
            data: {
                preference: guestPreference as UserPreference,
                accounts: [],
                player: null,
            } as UserProfile,
        }
    }

    const db = useDrizzle()
    const config = useRuntimeConfig()
    const session = await requireUserSession(event)

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

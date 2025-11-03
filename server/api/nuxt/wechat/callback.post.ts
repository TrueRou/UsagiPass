import { ServerCredentialsStrategy } from '~~/server/database/schema'

export default defineEventHandler(async (event) => {
    const userId = (await useUser(event)).id
    const db = useDrizzle()
    const config = useRuntimeConfig()

    const body = ((await readBody<{
        code?: string
        r?: string
        t?: string
        state?: string
    }>(event)) ?? {}) as {
        code?: string
        r?: string
        t?: string
        state?: string
    }

    const requiredKeys: (keyof typeof body)[] = ['code', 'r', 't', 'state']
    const missingKeys = requiredKeys.filter(key => !body[key] || body[key]?.toString().trim() === '')
    if (missingKeys.length) {
        throw createError({
            statusCode: 400,
            message: `缺少必要参数: ${missingKeys.join(', ')}`,
        })
    }

    const accounts = await db
        .select({
            id: tables.userAccount.id,
            credentials: tables.userAccount.credentials,
            serverId: tables.server.id,
            serverName: tables.server.name,
            serverIdentifier: tables.server.identifier,
            credentialsStrategy: tables.server.credentialsStrategy,
            credentialsField: tables.server.credentialsField,
        })
        .from(tables.userAccount)
        .innerJoin(
            tables.server,
            eq(tables.userAccount.serverId, tables.server.id),
        )
        .where(
            and(
                eq(tables.userAccount.userId, userId),
                eq(tables.userAccount.enabled, true),
            ),
        )

    if (!accounts.length) {
        throw createError({
            statusCode: 400,
            statusMessage: '请先在偏好设置中添加至少一个开启的查分器账号',
        })
    }

    // 获取微信服务号玩家标识
    const identifierResponse = await $fetch<{
        code: number
        message: string
        data?: { data: any }
    }>(`${config.otogeApi}/maimai/wechat/identifiers`, {
        method: 'GET',
        query: {
            code: body.code,
            r: body.r,
            t: body.t,
            state: body.state,
        },
    })

    if (identifierResponse.code !== 200 || !identifierResponse.data) {
        throw createError({
            statusCode: 500,
            message: '获取微信服务号玩家标识失败',
        })
    }

    // 构造链式更新的 target 请求体
    const targetBody = accounts.reduce((dict, val) => {
        const target = dict[val.serverIdentifier] = {} as UpdatesChainTargetBody[string]
        if (val.credentialsStrategy === ServerCredentialsStrategy.PLAIN) {
            target[val.credentialsField as ServerCredentialsField] = val.credentials
        }
        return dict
    }, ({} as UpdatesChainTargetBody))

    // 发起链式更新请求
    const updateResponse = await $fetch<{
        code: number
        message: string
        data?: { data: any }
    }>(`${config.otogeApi}/maimai/updates_chain`, {
        method: 'POST',
        body: {
            source: {
                wechat: {
                    credentials: identifierResponse.data.data.credentials,
                },
            },
            target: targetBody,
        },
    })

    if (updateResponse.code !== 200 || !updateResponse.data) {
        throw createError({
            statusCode: 500,
            message: '查分器更新请求失败',
        })
    }

    // 发起获取玩家信息请求
    const playerResponse = await $fetch<{
        code: number
        message: string
        data?: { data: any }
    }>(`${config.otogeApi}/maimai/updates_chain`, {
        method: 'GET',
        query: {
            _t: identifierResponse.data.data.credentials._t,
            userId: identifierResponse.data.data.credentials.userId,
        },
    })

    if (playerResponse.code !== 200 || !playerResponse.data) {
        throw createError({
            statusCode: 500,
            message: '获取玩家信息请求失败',
        })
    }

    await db.insert(tables.userRating).values({
        userId,
        rating: playerResponse.data.data.rating,
        name: playerResponse.data.data.name,
    }).onConflictDoUpdate({
        target: tables.userRating.userId,
        set: {
            rating: playerResponse.data.data.rating,
            name: playerResponse.data.data.name,
            updatedAt: new Date(),
        },
    })

    return {
        code: 200,
        message: '请求成功',
        data: updateResponse.data.data,
    }
})

import { ServerCredentialsStrategy } from '~~/server/database/schema'

export default defineEventHandler(async (event) => {
    const session = await requireUserSession(event)
    const db = useDrizzle()

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
        return {
            code: 400,
            message: `缺少必要参数: ${missingKeys.join(', ')}`,
            data: null,
        }
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
                eq(tables.userAccount.userId, session.user.id),
                eq(tables.userAccount.enabled, true),
            ),
        )

    // 获取微信服务号玩家标识
    const identifierResponse = await $fetch<{
        code: number
        message: string
        data?: { credentials: any }
    }>(`/api/otoge/maimai/wechat/identifiers`, {
        method: 'GET',
        ignoreResponseError: true,
        query: {
            code: body.code,
            r: body.r,
            t: body.t,
            state: body.state,
        },
    })

    if (identifierResponse.code !== 200 || !identifierResponse.data) {
        return {
            code: 500,
            message: '获取微信服务号玩家标识请求失败',
            data: null,
        }
    }

    // 有绑定账号则发起链式更新请求
    let chainResults = {}
    if (accounts.length !== 0) {
        const targetBody = accounts.reduce((dict, val) => {
            const target = dict[val.serverIdentifier] = {} as UpdatesChainTargetBody[string]
            if (val.credentialsStrategy === ServerCredentialsStrategy.PLAIN) {
                target[val.credentialsField as ServerCredentialsField] = val.credentials
            }
            return dict
        }, ({} as UpdatesChainTargetBody))

        const updateResponse = await $fetch<{
            code: number
            message: string
            data?: any
        }>(`/api/otoge/maimai/updates_chain`, {
            method: 'POST',
            ignoreResponseError: true,
            body: {
                source: {
                    wechat: {
                        credentials: identifierResponse.data.credentials,
                    },
                },
                target: targetBody,
            },
        })

        chainResults = updateResponse.data || {}

        if (updateResponse.code !== 200 || !updateResponse.data) {
            return {
                code: 500,
                message: '查分器更新请求失败',
                data: null,
            }
        }
    }

    // 发起获取玩家信息请求
    const playerResponse = await $fetch<{
        code: number
        message: string
        data?: { name: string, rating: number }
    }>(`/api/otoge/maimai/wechat/players`, {
        method: 'GET',
        ignoreResponseError: true,
        query: {
            _t: identifierResponse.data.credentials._t,
            userId: identifierResponse.data.credentials.userId,
        },
    })

    if (playerResponse.code !== 200 || !playerResponse.data) {
        return {
            code: 500,
            message: '获取玩家信息请求失败',
            data: null,
        }
    }

    // 保存玩家评级信息
    await db.insert(tables.userRating).values({
        userId: session.user.id,
        rating: playerResponse.data.rating,
        name: playerResponse.data.name,
    }).onConflictDoUpdate({
        target: tables.userRating.userId,
        set: {
            rating: playerResponse.data.rating,
            name: playerResponse.data.name,
            updatedAt: new Date(),
        },
    })

    return {
        code: 200,
        message: '请求成功',
        data: chainResults,
    }
})

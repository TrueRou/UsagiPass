import { randomUUID } from 'node:crypto'

export default defineEventHandler(async (event) => {
    const session = await requireUserSession(event)
    const provider = getRouterParam(event, 'provider')
    const body = (await readBody<{ code?: string, state?: string }>(event)) ?? {}

    if (!isProberOAuthServer(provider) || !body.code || !body.state) {
        return {
            code: 400,
            message: '授权回调参数无效，请重新授权',
            data: null,
        }
    }

    const response = await $fetch<{
        code: number
        message: string
        data?: { credential: string, username: string, display_name: string, context: Record<string, string> }
    }>(`/api/maimai/oauth/${provider}/callback`, {
        method: 'POST',
        ignoreResponseError: true,
        body: { code: body.code, state: body.state },
    })

    if (response.code !== 200 || !response.data) {
        return {
            code: 400,
            message: response.message || '授权失败，请稍后再试',
            data: null,
        }
    }

    const grant = response.data
    // 授权必须由当前登录用户发起，防止他人把自己的授权回调链接转发给受害者
    if (grant.context.app !== 'usagipass' || grant.context.user_id !== session.user.id) {
        await revokeProberOAuthCredential(grant.credential)
        return {
            code: 403,
            message: '授权请求不属于当前账号，请重新授权',
            data: null,
        }
    }

    const db = useDrizzle()
    const server = await db.query.server.findFirst({
        where: eq(tables.server.identifier, provider),
    })
    if (!server) {
        await revokeProberOAuthCredential(grant.credential)
        return {
            code: 400,
            message: '查分器不存在',
            data: null,
        }
    }

    // 同一查分器只保留一个账号：授权绑定替换该查分器下已有的账号
    const replaced = await db.transaction(async (tx) => {
        const existing = await tx.query.userAccount.findMany({
            where: and(
                eq(tables.userAccount.userId, session.user.id),
                eq(tables.userAccount.serverId, server.id),
            ),
        })
        await tx.delete(tables.userAccount).where(and(
            eq(tables.userAccount.userId, session.user.id),
            eq(tables.userAccount.serverId, server.id),
        ))
        await tx.insert(tables.userAccount).values({
            id: randomUUID(),
            userId: session.user.id,
            serverId: server.id,
            credentials: grant.credential,
            enabled: true,
        })
        return existing
    })
    await Promise.all(replaced.map(account => revokeProberOAuthCredential(account.credentials)))

    const accounts = await db.query.userAccount.findMany({
        where: eq(tables.userAccount.userId, session.user.id),
    })

    return {
        code: 200,
        message: `已绑定${server.name}账号`,
        data: { accounts, username: grant.display_name || grant.username },
    }
})

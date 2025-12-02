import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'

import * as schema from '../database/schema'

export { and, eq, or, sql } from 'drizzle-orm'

export const tables = schema

let _pool: Pool | null = null

function getPool() {
    if (!_pool) {
        const databaseURL = useRuntimeConfig().usagipass.databaseURL
        _pool = new Pool({
            connectionString: databaseURL,
            max: 20, // 最大连接数
            idleTimeoutMillis: 30000, // 空闲连接超时时间（30秒）
            connectionTimeoutMillis: 2000, // 连接超时时间（2秒）
        })
    }
    return _pool
}

export function useDrizzle() {
    return drizzle(getPool(), { schema })
}

export type Server = typeof schema.server.$inferSelect
export type UserAccount = typeof schema.userAccount.$inferSelect
export type UserPreference = typeof schema.userPreference.$inferSelect
export type UserRating = typeof schema.userRating.$inferSelect

export interface UserProfile {
    preference: UserPreference
    accounts: UserAccount[]
    player: UserRating | null
}

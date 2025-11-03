import { drizzle } from 'drizzle-orm/node-postgres'

import * as schema from '../database/schema'

export { and, eq, or, sql } from 'drizzle-orm'

export const tables = schema

const config = useRuntimeConfig()

export function useDrizzle() {
    return drizzle(config.databaseUrl || '', { schema })
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

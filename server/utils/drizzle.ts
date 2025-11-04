import { drizzle } from 'drizzle-orm/node-postgres'

import * as schema from '../database/schema'

export { and, eq, or, sql } from 'drizzle-orm'

export const tables = schema

export function useDrizzle() {
    return drizzle(useRuntimeConfig().usagipass.databaseURL || '', { schema })
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

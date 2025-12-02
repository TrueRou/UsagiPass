import consola from 'consola'
import { drizzle } from 'drizzle-orm/node-postgres'
import { migrate } from 'drizzle-orm/node-postgres/migrator'
import { defineNuxtPrepareHandler } from 'nuxt-prepare/config'
import { Pool } from 'pg'

export default defineNuxtPrepareHandler(async () => {
    consola.info('Running database migrations...')

    const databaseURL = process.env.NUXT_USAGIPASS_DATABASE_URL

    if (!databaseURL) {
        consola.error('NUXT_USAGIPASS_DATABASE_URL environment variable is not set')
        process.exit(1)
    }

    const pool = new Pool({
        connectionString: databaseURL,
        max: 1, // 迁移时只需要一个连接
    })

    const db = drizzle(pool)

    try {
        await migrate(db, { migrationsFolder: './server/database/migrations' })
        consola.success('Database migrated successfully')
    }
    catch (err) {
        consola.error('Database migration failed:', err)
        process.exit(1)
    }
    finally {
        await pool.end()
    }

    return {}
})

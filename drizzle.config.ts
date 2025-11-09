import { defineConfig } from 'drizzle-kit'

export default defineConfig({
    dialect: 'postgresql',
    schema: './server/database/schema.ts',
    out: './server/database/migrations',
    dbCredentials: {
        url: process.env.NUXT_USAGIPASS_DATABASE_URL || 'postgresql://postgres:password@localhost:5432/usagipass',
    },
})

import { join } from 'node:path/posix'
import { count } from 'drizzle-orm'
import { drizzle } from 'drizzle-orm/node-postgres'
import { migrate } from 'drizzle-orm/node-postgres/migrator'
import { Pool } from 'pg'
import * as schema from '../database/schema'

async function seedInitialData(db: ReturnType<typeof useDrizzle>) {
    // 检查 server 表是否为空
    const serverCount = await db.select({ count: count() }).from(schema.server)
    if (serverCount[0].count === 0) {
        await db.insert(schema.server).values([
            {
                id: 1,
                name: '水鱼查分器',
                description: 'DivingFish - 舞萌 DX 查分器',
                identifier: 'divingfish',
                tipsTitle: '水鱼查分器使用指南',
                tipsDesc: '如果您没有使用过水鱼查分器，开始之前，建议您先注册一个查分器账户。然后就可以利用 UsagiPass 代理快速导入您的成绩。登录水鱼后，点击编辑个人资料，复制成绩导入 Token，填入下方即可。',
                tipsUrl: 'https://www.diving-fish.com/maimaidx/prober/',
                credentialsStrategy: 'plain',
                credentialsField: 'credentials',
                credentialsName: '水鱼 Import-Token',
            },
            {
                id: 2,
                name: '落雪查分器',
                description: '落雪咖啡屋 - maimai DX 查分器',
                identifier: 'lxns',
                tipsTitle: '落雪查分器使用指南',
                tipsDesc: '使用落雪查分器之前，请先注册落雪账号，并且通过落雪官方途径至少上传一次成绩。完成后，进入账号详情，点击第三方应用，复制个人 API 密钥，填入下方即可。',
                tipsUrl: 'https://maimai.lxns.net/',
                credentialsStrategy: 'plain',
                credentialsField: 'credentials',
                credentialsName: '个人 API 密钥',
            },
        ])
        console.info('No servers found in database. Seeded initial server data.')
    }
}

export default defineNitroPlugin((_nitroApp) => {
    const databaseURL = useRuntimeConfig().usagipass.databaseURL

    if (!databaseURL) {
        console.error('NUXT_USAGIPASS_DATABASE_URL environment variable is not set')
        process.exit(1)
    }

    try {
        const pool = new Pool({ connectionString: databaseURL, max: 1 })
        const db = drizzle(pool, { schema })

        const migrationFolder = join(process.cwd(), 'server', 'database', 'migrations')
        migrate(db, { migrationsFolder: migrationFolder }).then(() => seedInitialData(db))
    }
    catch (error) {
        console.error('Failed to run migrations:', error)
        process.exit(1)
    }
})

import { drizzle } from 'drizzle-orm/node-postgres'
import * as schema from './schema'

async function seed() {
    const db = drizzle(process.env.NUXT_USAGIPASS_DATABASE_URL || '', { schema })
    await db.delete(schema.server)

    await db.insert(schema.server).values([
        {
            id: 1,
            name: '水鱼查分器',
            description: 'DivingFish - 舞萌 DX 查分器',
            identifier: 'divingfish',
            tipsTitle: '水鱼查分器使用指南',
            tipsDesc: '如果您没有使用过水鱼查分器，开始之前，建议您先注册一个查分器账户。然后就可以利用UsagiPass代理快速导入您的成绩。登录水鱼后，点击编辑个人资料，复制成绩导入Token，填入下方即可。',
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
            tipsDesc: '使用落雪查分器之前，请先注册落雪账号，并且使用落雪官方至少上传一次成绩。完成后，进入账号详情，点击第三方应用，复制个人API密钥，填入下方即可。',
            tipsUrl: 'https://maimai.lxns.net/',
            credentialsStrategy: 'plain',
            credentialsField: 'credentials',
            credentialsName: '个人 API 密钥',
        },
    ])

    console.log('Database seeded successfully.')
}

seed().catch((err) => {
    console.error('Error seeding database:', err)
    process.exit(1)
})

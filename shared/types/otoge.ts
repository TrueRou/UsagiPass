export interface MaimaiCharacter {
    /** 角色ID */
    id: number
    /** 角色名 */
    name: string
    /** 版本 */
    version: string
}

export interface OngekiCard {
    /** 卡片ID */
    id: number
    /** 卡片名 */
    name: string
    /** 角色ID */
    character_id: number
    /** 角色名 */
    character_name: string
    /** 稀有度 */
    rarity: string
    /** 属性 */
    attribute: string
    /** 称号 */
    description?: string | null
    /** 代表 */
    representative?: string | null
    /** 年级ID */
    grade_id: number
    /** 年级 */
    grade?: string | null
    /** 组合ID */
    group_id: number
    /** 组合 */
    group?: string | null
    /** 技能ID */
    skill_id: number
    /** 技能 */
    skill: string
    /** 超解花技能ID */
    super_skill_id: number
    /** 超解花技能 */
    super_skill: string
    /** 版本 */
    version: string
    /** 卡面数字 */
    version_number: string
    /** 版权名称 */
    copyright?: string | null
    /** 3D模型名称 */
    model_name?: string | null
    /** 0星攻击力 */
    attack_power_0: number
    /** 1星攻击力 */
    attack_power_1: number
    /** 2星攻击力 */
    attack_power_2: number
    /** 3星攻击力 */
    attack_power_3: number
    /** 4星攻击力 */
    attack_power_4: number
    /** 5星攻击力 */
    attack_power_5: number
    /** 7星攻击力 */
    attack_power_7?: number | null
    /** 9星攻击力 */
    attack_power_9?: number | null
    /** 11星攻击力 */
    attack_power_11?: number | null
    /** MAX攻击力 */
    attack_power_max: number
}

export interface OngekiSkill {
    /** 技能ID */
    id: number
    /** 技能类型 */
    type: string
    /** 技能详细 */
    details: string
}

export interface ChunithmCharacter {
    /** 角色ID */
    id: number
    /** 角色名 */
    name: string
    /** 稀有度 */
    rarity: number
    /** 标签种类 */
    tag_type: number
    /** miss值 */
    miss: number
    /** combo值 */
    combo: number
    /** chain值 */
    chain: number
    /** 技能名 */
    skill_name: string
    /** 技能描述 */
    skill_description: string
}

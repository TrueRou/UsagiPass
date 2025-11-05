import { boolean, integer, pgTable, serial, text, timestamp, uuid } from 'drizzle-orm/pg-core'

export enum ServerCredentialsStrategy {
    PLAIN = 'plain',
}

export const server = pgTable('tbl_server', {
    id: serial('id').primaryKey(),
    name: text('name').notNull(),
    description: text('description').notNull(),
    identifier: text('identifier').notNull(),
    tipsTitle: text('tips_title').notNull(),
    tipsDesc: text('tips_desc').notNull(),
    tipsUrl: text('tips_url').notNull(),
    credentialsStrategy: text('credentials_strategy').notNull(),
    credentialsField: text('credentials_field').notNull(),
    credentialsName: text('credentials_name').notNull().default(''),
})

export const userPreference = pgTable('tbl_preference', {
    userId: uuid('user_id').primaryKey(),
    maimaiVersion: text('maimai_version').notNull().default(''),
    simplifiedCode: text('simplified_code').notNull().default(''),
    characterName: text('character_name').notNull().default(''),
    friendCode: text('friend_code').notNull().default(''),
    displayName: text('display_name').notNull().default(''),
    dxRating: text('dx_rating').notNull().default(''),
    qrSize: integer('qr_size').notNull().default(15),
    maskType: integer('mask_type').notNull().default(0),
    playerInfoColor: text('player_info_color').notNull().default('#ffffff'),
    charaInfoColor: text('chara_info_color').notNull().default('#fee37c'),
    showDxRating: boolean('show_dx_rating').notNull().default(true),
    showDisplayName: boolean('show_display_name').notNull().default(true),
    showFriendCode: boolean('show_friend_code').notNull().default(true),
    showDate: boolean('show_date').notNull().default(true),
    characterId: text('character_id').notNull(),
    maskId: text('mask_id').notNull(),
    backgroundId: text('background_id').notNull(),
    frameId: text('frame_id').notNull(),
    passnameId: text('passname_id').notNull(),
})

export const userRating = pgTable('tbl_rating', {
    userId: uuid('user_id').primaryKey(),
    name: text('name').notNull().default(''),
    rating: integer('rating').notNull().default(0),
    friendCode: text('friend_code').notNull().default(''),
    updatedAt: timestamp('updated_at').notNull().defaultNow(),
})

export const userAccount = pgTable('tbl_account', {
    id: uuid('id').primaryKey(),
    userId: uuid('user_id').notNull(),
    serverId: integer('server_id').notNull().references(() => server.id),
    credentials: text('credentials').notNull(),
    enabled: boolean('enabled').notNull().default(true),
    createdAt: timestamp('created_at').notNull().defaultNow(),
    updatedAt: timestamp('updated_at').notNull().defaultNow(),
})

ALTER TABLE "tbl_preference" ADD COLUMN "player_info_color" text DEFAULT '#ffffff' NOT NULL;--> statement-breakpoint
ALTER TABLE "tbl_rating" ADD COLUMN "name" text DEFAULT '' NOT NULL;--> statement-breakpoint
ALTER TABLE "tbl_rating" ADD COLUMN "friend_code" text DEFAULT '' NOT NULL;
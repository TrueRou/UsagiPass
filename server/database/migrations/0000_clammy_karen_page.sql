CREATE TABLE "tbl_server" (
	"id" serial PRIMARY KEY NOT NULL,
	"name" text NOT NULL,
	"description" text NOT NULL,
	"identifier" text NOT NULL,
	"tips_title" text NOT NULL,
	"tips_desc" text NOT NULL,
	"tips_url" text NOT NULL,
	"credentials_strategy" text NOT NULL,
	"credentials_field" text NOT NULL,
	"credentials_name" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "tbl_account" (
	"id" uuid PRIMARY KEY NOT NULL,
	"user_id" uuid NOT NULL,
	"server_id" integer NOT NULL,
	"credentials" text NOT NULL,
	"enabled" boolean DEFAULT true NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "tbl_preference" (
	"user_id" uuid PRIMARY KEY NOT NULL,
	"maimai_version" text DEFAULT '' NOT NULL,
	"simplified_code" text DEFAULT '' NOT NULL,
	"character_name" text DEFAULT '' NOT NULL,
	"friend_code" text DEFAULT '' NOT NULL,
	"display_name" text DEFAULT '' NOT NULL,
	"dx_rating" text DEFAULT '' NOT NULL,
	"qr_size" integer DEFAULT 15 NOT NULL,
	"mask_type" integer DEFAULT 0 NOT NULL,
	"player_info_color" text DEFAULT '#ffffff' NOT NULL,
	"chara_info_color" text DEFAULT '#fee37c' NOT NULL,
	"show_dx_rating" boolean DEFAULT true NOT NULL,
	"show_display_name" boolean DEFAULT true NOT NULL,
	"show_friend_code" boolean DEFAULT true NOT NULL,
	"show_date" boolean DEFAULT true NOT NULL,
	"character_id" text NOT NULL,
	"mask_id" text NOT NULL,
	"background_id" text NOT NULL,
	"frame_id" text NOT NULL,
	"passname_id" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "tbl_rating" (
	"user_id" uuid PRIMARY KEY NOT NULL,
	"name" text DEFAULT '' NOT NULL,
	"rating" integer DEFAULT 0 NOT NULL,
	"friend_code" text DEFAULT '' NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "tbl_account" ADD CONSTRAINT "tbl_account_server_id_tbl_server_id_fk" FOREIGN KEY ("server_id") REFERENCES "public"."tbl_server"("id") ON DELETE no action ON UPDATE no action;
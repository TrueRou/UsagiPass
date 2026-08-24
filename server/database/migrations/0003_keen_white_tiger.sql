CREATE TABLE "tbl_metadata" (
	"key" text PRIMARY KEY NOT NULL,
	"value" text NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL,
	"updated_by" uuid
);
INSERT INTO "tbl_metadata" ("key", "value") VALUES ('maimaiVersion', '[maimaiDX]CN1.51-H');

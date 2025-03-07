"""add card tables

Revision ID: dd0c9bfac74a
Revises: 9cdcf6f8ca8c
Create Date: 2025-03-08 15:02:48.873088

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = "dd0c9bfac74a"
down_revision: Union[str, None] = "9cdcf6f8ca8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "card_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mai_userid", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("mai_rating", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_card_users_mai_userid"), "card_users", ["mai_userid"], unique=True)
    op.create_table(
        "cards",
        sa.Column("uuid", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("phone_number", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["card_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_cards_card_id"), "cards", ["card_id"], unique=True)
    op.create_index(op.f("ix_cards_phone_number"), "cards", ["phone_number"], unique=False)
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("song_id", sa.Integer(), nullable=False),
        sa.Column("level_index", sa.Enum("BASIC", "ADVANCED", "EXPERT", "MASTER", "ReMASTER", name="levelindex"), nullable=False),
        sa.Column("achievements", sa.Float(), nullable=True),
        sa.Column("fc", sa.Enum("APP", "AP", "FCP", "FC", name="fctype"), nullable=True),
        sa.Column("fs", sa.Enum("SYNC", "FS", "FSP", "FSD", "FSDP", name="fstype"), nullable=True),
        sa.Column("dx_score", sa.Integer(), nullable=True),
        sa.Column("dx_rating", sa.Float(), nullable=True),
        sa.Column(
            "rate", sa.Enum("SSSP", "SSS", "SSP", "SS", "SP", "S", "AAA", "AA", "A", "BBB", "BB", "B", "C", "D", name="ratetype"), nullable=False
        ),
        sa.Column("type", sa.Enum("STANDARD", "DX", "UTAGE", name="songtype"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["card_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scores_song_id"), "scores", ["song_id"], unique=False)
    op.create_index(op.f("ix_scores_user_id"), "scores", ["user_id"], unique=False)
    op.create_table(
        "card_preferences",
        sa.Column("maimai_version", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("simplified_code", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("character_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("friend_code", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("dx_rating", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("qr_size", sa.Integer(), nullable=False),
        sa.Column("mask_type", sa.Integer(), nullable=False),
        sa.Column("uuid", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("character_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("background_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("frame_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("passname_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(["background_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["character_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["frame_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["passname_id"], ["images.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uuid"], ["cards.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.drop_constraint("user_preferences_ibfk_4", "user_preferences", type_="foreignkey")
    op.drop_constraint("user_preferences_ibfk_3", "user_preferences", type_="foreignkey")
    op.drop_constraint("user_preferences_ibfk_2", "user_preferences", type_="foreignkey")
    op.drop_constraint("user_preferences_ibfk_1", "user_preferences", type_="foreignkey")
    op.create_foreign_key(None, "user_preferences", "images", ["background_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "user_preferences", "users", ["username"], ["username"])
    op.create_foreign_key(None, "user_preferences", "images", ["frame_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "user_preferences", "images", ["character_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "user_preferences", "images", ["passname_id"], ["id"], ondelete="SET NULL")
    op.add_column("users", sa.Column("privilege", sa.Enum("BANNED", "NORMAL", "ADMIN", name="privilege"), nullable=False, server_default="NORMAL"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "privilege")
    op.drop_constraint(None, "user_preferences", type_="foreignkey")
    op.drop_constraint(None, "user_preferences", type_="foreignkey")
    op.drop_constraint(None, "user_preferences", type_="foreignkey")
    op.drop_constraint(None, "user_preferences", type_="foreignkey")
    op.drop_constraint(None, "user_preferences", type_="foreignkey")
    op.create_foreign_key("user_preferences_ibfk_1", "user_preferences", "images", ["character_id"], ["id"])
    op.create_foreign_key("user_preferences_ibfk_2", "user_preferences", "images", ["frame_id"], ["id"])
    op.create_foreign_key("user_preferences_ibfk_3", "user_preferences", "images", ["passname_id"], ["id"])
    op.create_foreign_key("user_preferences_ibfk_4", "user_preferences", "images", ["background_id"], ["id"])
    op.drop_table("card_preferences")
    op.drop_index(op.f("ix_scores_user_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_song_id"), table_name="scores")
    op.drop_table("scores")
    op.drop_index(op.f("ix_cards_phone_number"), table_name="cards")
    op.drop_index(op.f("ix_cards_card_id"), table_name="cards")
    op.drop_table("cards")
    op.drop_index(op.f("ix_card_users_mai_userid"), table_name="card_users")
    op.drop_table("card_users")
    # ### end Alembic commands ###

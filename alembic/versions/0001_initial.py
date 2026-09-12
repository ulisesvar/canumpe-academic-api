"""initial schema: student identities and api keys

Revision ID: 0001
Revises:
Create Date: 2026-09-11

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None


def upgrade() -> None:
    op.create_table(
        "student_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_number", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="student"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("account_number", name="uq_student_identities_account_number"),
    )
    op.create_index(
        "ix_student_identities_account_number", "student_identities", ["account_number"]
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key_id", sa.String(length=32), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column(
            "student_id",
            sa.Integer(),
            sa.ForeignKey("student_identities.id"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("key_id", name="uq_api_keys_key_id"),
    )
    op.create_index("ix_api_keys_key_id", "api_keys", ["key_id"])
    op.create_index("ix_api_keys_student_id", "api_keys", ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_student_id", table_name="api_keys")
    op.drop_index("ix_api_keys_key_id", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index("ix_student_identities_account_number", table_name="student_identities")
    op.drop_table("student_identities")

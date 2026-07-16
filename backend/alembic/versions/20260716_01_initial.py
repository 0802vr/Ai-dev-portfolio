"""Initial contacts schema.

Revision ID: 20260716_01
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

delivery_status = sa.Enum("pending", "sent", "failed", "skipped", name="deliverystatus")


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "contacts" not in inspector.get_table_names():
        op.create_table(
            "contacts",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(80), nullable=False),
            sa.Column("phone", sa.String(30), nullable=False),
            sa.Column("email", sa.String(254), nullable=False),
            sa.Column("comment", sa.Text(), nullable=False),
            sa.Column("ip_hash", sa.String(64), nullable=False),
            sa.Column("ai_category", sa.String(40), nullable=False),
            sa.Column("ai_sentiment", sa.String(20), nullable=False),
            sa.Column("ai_priority", sa.String(20), nullable=False),
            sa.Column("ai_summary", sa.String(300), nullable=False),
            sa.Column("ai_reply", sa.Text(), nullable=False),
            sa.Column("ai_used_fallback", sa.Boolean(), nullable=False),
            sa.Column("owner_delivery", delivery_status, nullable=False),
            sa.Column("user_delivery", delivery_status, nullable=False),
            sa.Column("delivery_error", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_contacts_email", "contacts", ["email"])
        op.create_index("ix_contacts_ip_hash", "contacts", ["ip_hash"])
        op.create_index("ix_contacts_created_at", "contacts", ["created_at"])


def downgrade() -> None:
    op.drop_table("contacts")
    delivery_status.drop(op.get_bind(), checkfirst=True)


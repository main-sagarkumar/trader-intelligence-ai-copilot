"""Create authentication and authorization tables.

Revision ID: 001_create_authentication_tables
Revises:
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "001_create_authentication_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create local identity, RBAC, ownership, and refresh-token tables."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "roles",
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.bulk_insert(
        sa.table("roles", sa.column("name", sa.String(length=32))),
        [
            {"name": "trader"},
            {"name": "analyst"},
            {"name": "risk_manager"},
            {"name": "admin"},
        ],
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_name", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["role_name"], ["roles.name"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_name"),
    )
    op.create_table(
        "trader_access",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("trader_id", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "trader_id"),
    )
    op.create_index(
        "ix_trader_access_trader_id",
        "trader_access",
        ["trader_id"],
        unique=False,
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )
    op.create_index(
        "ix_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove local identity, RBAC, ownership, and refresh-token tables."""
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_trader_access_trader_id", table_name="trader_access")
    op.drop_table("trader_access")
    op.drop_table("user_roles")
    op.drop_table("roles")
    op.drop_table("users")

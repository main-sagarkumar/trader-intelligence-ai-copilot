"""Remove the unused risk manager role.

Revision ID: 002_remove_risk_manager_role
Revises: 001_create_authentication_tables
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "002_remove_risk_manager_role"
down_revision = "001_create_authentication_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Retain only the trader, analyst, and admin role set."""
    op.execute(sa.text("DELETE FROM roles WHERE name = 'risk_manager'"))


def downgrade() -> None:
    """Restore the removed role if this migration is rolled back."""
    op.bulk_insert(
        sa.table("roles", sa.column("name", sa.String(length=32))),
        [{"name": "risk_manager"}],
    )

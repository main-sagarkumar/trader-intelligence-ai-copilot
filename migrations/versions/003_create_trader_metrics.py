"""Create the structured trader metrics table for clean installations.

Revision ID: 003_create_trader_metrics
Revises: 002_remove_risk_manager_role
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "003_create_trader_metrics"
down_revision = "002_remove_risk_manager_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the business-data table when provisioning a fresh database."""
    op.create_table(
        "trader_metrics",
        sa.Column("trader_id", sa.Text(), primary_key=True),
        sa.Column("persona", sa.Text(), nullable=True),
        sa.Column("account_size", sa.BigInteger(), nullable=True),
        sa.Column("final_balance", sa.Float(), nullable=True),
        sa.Column("total_trades", sa.BigInteger(), nullable=True),
        sa.Column("total_pnl", sa.Float(), nullable=True),
        sa.Column("avg_pnl", sa.Float(), nullable=True),
        sa.Column("win_rate", sa.Float(), nullable=True),
        sa.Column("avg_holding_minutes", sa.Float(), nullable=True),
        sa.Column("avg_leverage", sa.Float(), nullable=True),
        sa.Column("avg_risk_pct", sa.Float(), nullable=True),
        sa.Column("stop_loss_usage_rate", sa.Float(), nullable=True),
        sa.Column("overnight_position_rate", sa.Float(), nullable=True),
        sa.Column("roi_pct", sa.Float(), nullable=True),
        sa.Column("cluster", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    """Remove the structured trader metrics table."""
    op.drop_table("trader_metrics")

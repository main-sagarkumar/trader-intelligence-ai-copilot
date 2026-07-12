"""SQLAlchemy ORM mapping for trader metrics."""

from sqlalchemy import BigInteger, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from trader_intelligence_ai_copilot.database.base import Base


class TraderMetricsModel(Base):
    """Persistence model for the existing ``trader_metrics`` table."""

    __tablename__ = "trader_metrics"

    trader_id: Mapped[str] = mapped_column(Text, primary_key=True)
    persona: Mapped[str | None] = mapped_column(Text)
    account_size: Mapped[int | None] = mapped_column(BigInteger)
    final_balance: Mapped[float | None] = mapped_column(Float)
    total_trades: Mapped[int | None] = mapped_column(BigInteger)
    total_pnl: Mapped[float | None] = mapped_column(Float)
    avg_pnl: Mapped[float | None] = mapped_column(Float)
    win_rate: Mapped[float | None] = mapped_column(Float)
    avg_holding_minutes: Mapped[float | None] = mapped_column(Float)
    avg_leverage: Mapped[float | None] = mapped_column(Float)
    avg_risk_pct: Mapped[float | None] = mapped_column(Float)
    stop_loss_usage_rate: Mapped[float | None] = mapped_column(Float)
    overnight_position_rate: Mapped[float | None] = mapped_column(Float)
    roi_pct: Mapped[float | None] = mapped_column(Float)
    cluster: Mapped[int | None] = mapped_column(BigInteger)

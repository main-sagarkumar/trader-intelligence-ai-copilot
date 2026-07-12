"""Domain model for a trader's performance profile."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraderProfile:
    """Structured trader metrics used by application services."""

    trader_id: str
    persona: str | None
    account_size: int | None
    final_balance: float | None
    total_trades: int | None
    total_pnl: float | None
    avg_pnl: float | None
    win_rate: float | None
    avg_holding_minutes: float | None
    avg_leverage: float | None
    avg_risk_pct: float | None
    stop_loss_usage_rate: float | None
    overnight_position_rate: float | None
    roi_pct: float | None
    cluster: int | None

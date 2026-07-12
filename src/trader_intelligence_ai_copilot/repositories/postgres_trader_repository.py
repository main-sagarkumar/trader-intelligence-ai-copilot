"""PostgreSQL implementation of the trader repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from trader_intelligence_ai_copilot.database.models import TraderMetricsModel
from trader_intelligence_ai_copilot.repositories.trader_repository import TraderRepository
from trader_intelligence_ai_copilot.trader import TraderProfile


class PostgresTraderRepository(TraderRepository):
    """Retrieve trader profiles from PostgreSQL through SQLAlchemy ORM."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a request-scoped database session."""
        self._session = session

    def get_by_id(self, trader_id: str) -> TraderProfile | None:
        """Return a trader profile by its unique identifier, if it exists."""
        trader_metrics = self._session.scalar(
            select(TraderMetricsModel).where(
                TraderMetricsModel.trader_id == trader_id
            )
        )

        if trader_metrics is None:
            return None

        return self._to_profile(trader_metrics)

    @staticmethod
    def _to_profile(trader_metrics: TraderMetricsModel) -> TraderProfile:
        """Map the persistence model to the trader domain model."""
        return TraderProfile(
            trader_id=trader_metrics.trader_id,
            persona=trader_metrics.persona,
            account_size=trader_metrics.account_size,
            final_balance=trader_metrics.final_balance,
            total_trades=trader_metrics.total_trades,
            total_pnl=trader_metrics.total_pnl,
            avg_pnl=trader_metrics.avg_pnl,
            win_rate=trader_metrics.win_rate,
            avg_holding_minutes=trader_metrics.avg_holding_minutes,
            avg_leverage=trader_metrics.avg_leverage,
            avg_risk_pct=trader_metrics.avg_risk_pct,
            stop_loss_usage_rate=trader_metrics.stop_loss_usage_rate,
            overnight_position_rate=trader_metrics.overnight_position_rate,
            roi_pct=trader_metrics.roi_pct,
            cluster=trader_metrics.cluster,
        )

"""Trader repository contract."""

from abc import ABC, abstractmethod

from trader_intelligence_ai_copilot.trader import TraderProfile


class TraderRepository(ABC):
    """Interface for retrieving trader profiles."""

    @abstractmethod
    def get_by_id(self, trader_id: str) -> TraderProfile | None:
        """Return the profile for a trader, if it exists."""

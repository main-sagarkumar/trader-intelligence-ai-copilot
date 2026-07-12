"""Deterministic intent classification shared by runtime and evaluation."""

from typing import Literal


Route = Literal["trader", "generic", "both"]


class IntentRouter:
    TRADER_TERMS = ("my ", "cluster", "profile", "improve", "leverage", "pnl")
    GENERIC_TERMS = ("option", "volatility", "psychology", "revenge", "emotion")

    @classmethod
    def classify(cls, question: str) -> Route:
        normalized = question.lower()
        has_trader = any(term in normalized for term in cls.TRADER_TERMS)
        has_generic = any(term in normalized for term in cls.GENERIC_TERMS)
        if has_trader and has_generic:
            return "both"
        return "trader" if has_trader else "generic"

    @staticmethod
    def categories(route: Route) -> tuple[str, ...]:
        if route == "trader":
            return ("trader_intelligence",)
        if route == "generic":
            return ("options", "trading_psychology")
        return ("trader_intelligence", "options", "trading_psychology")

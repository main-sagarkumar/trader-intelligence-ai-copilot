"""Manually verify PostgreSQL trader profile retrieval."""

from trader_intelligence_ai_copilot.database.session import SessionLocal, get_engine
from trader_intelligence_ai_copilot.repositories import PostgresTraderRepository


def main() -> None:
    """Retrieve and print the known trader profile."""
    with SessionLocal(bind=get_engine()) as session:
        repository = PostgresTraderRepository(session)
        profile = repository.get_by_id("TRADER_101")

    if profile is None:
        raise RuntimeError("Expected trader TRADER_101 was not found.")

    print(profile)


if __name__ == "__main__":
    main()

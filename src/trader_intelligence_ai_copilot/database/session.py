"""SQLAlchemy engine and session management."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from trader_intelligence_ai_copilot.config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    """Create and cache the configured PostgreSQL SQLAlchemy engine."""
    settings = get_settings()
    database_url = settings.database.url.get_secret_value()

    if not database_url:
        raise RuntimeError("DATABASE_URL must be configured before using the database.")

    return create_engine(
        database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker[Session](
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after use."""
    session = SessionLocal(bind=get_engine())

    try:
        yield session
    finally:
        session.close()

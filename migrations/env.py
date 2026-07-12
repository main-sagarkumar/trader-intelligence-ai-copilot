"""Alembic migration environment."""

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trader_intelligence_ai_copilot.config.infra.database import DatabaseConfig
from trader_intelligence_ai_copilot.database.base import Base
from trader_intelligence_ai_copilot.database.models import (  # noqa: F401
    RefreshTokenModel,
    RoleModel,
    TraderAccessModel,
    TraderMetricsModel,
    UserModel,
    UserRoleModel,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = DatabaseConfig().url.get_secret_value()
if not database_url:
    raise RuntimeError("DATABASE_URL must be configured to run migrations.")

config.set_main_option("sqlalchemy.url", database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a database connection."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the configured database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

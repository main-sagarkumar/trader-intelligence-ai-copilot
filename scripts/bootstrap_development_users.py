"""Create development-only users, roles, and trader access grants."""

import os

from sqlalchemy import select

from trader_intelligence_ai_copilot.auth import PasswordService
from trader_intelligence_ai_copilot.database.models import (
    TraderAccessModel,
    TraderMetricsModel,
    UserModel,
    UserRoleModel,
)
from trader_intelligence_ai_copilot.database.session import SessionLocal, get_engine

ANALYST_EMAIL = "analyst@traders.local"
ADMIN_EMAIL = "admin@traders.local"


def required_environment_value(name: str) -> str:
    """Return a required bootstrap setting without echoing secrets."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set to run the bootstrap script.")

    return value


def ensure_user(
    session: SessionLocal,
    email: str,
    password: str,
    role_name: str,
    trader_ids: list[str],
) -> bool:
    """Create a user and its access grants when it does not already exist."""
    user = session.scalar(select(UserModel).where(UserModel.email == email))
    if user is not None:
        return False

    user = UserModel(
        email=email,
        password_hash=PasswordService.hash_password(password),
    )
    session.add(user)
    session.flush()
    session.add(UserRoleModel(user_id=user.id, role_name=role_name))
    session.add_all(
        TraderAccessModel(user_id=user.id, trader_id=trader_id)
        for trader_id in trader_ids
    )
    return True


def main() -> None:
    """Bootstrap local development users from explicit environment variables."""
    if os.getenv("ALLOW_DEVELOPMENT_BOOTSTRAP") != "true":
        raise RuntimeError(
            "Set ALLOW_DEVELOPMENT_BOOTSTRAP=true to create development users."
        )

    trader_password = required_environment_value("BOOTSTRAP_TRADER_PASSWORD")
    analyst_password = required_environment_value("BOOTSTRAP_ANALYST_PASSWORD")
    admin_password = required_environment_value("BOOTSTRAP_ADMIN_PASSWORD")

    with SessionLocal(bind=get_engine()) as session:
        if os.getenv("BOOTSTRAP_SAMPLE_TRADER") == "true":
            sample = session.get(TraderMetricsModel, "TRADER_101")
            if sample is None:
                session.add(
                    TraderMetricsModel(
                        trader_id="TRADER_101",
                        persona="Disciplined Growth Trader",
                        account_size=100000,
                        final_balance=108500,
                        total_trades=120,
                        total_pnl=8500,
                        avg_pnl=70.83,
                        win_rate=0.58,
                        avg_holding_minutes=95,
                        avg_leverage=2.4,
                        avg_risk_pct=1.2,
                        stop_loss_usage_rate=0.82,
                        overnight_position_rate=0.15,
                        roi_pct=8.5,
                        cluster=3,
                    )
                )
                session.flush()
        trader_ids = list(
            session.scalars(
                select(TraderMetricsModel.trader_id).where(
                    TraderMetricsModel.trader_id.is_not(None)
                )
            )
        )
        created_trader_users = sum(
            ensure_user(
                session=session,
                email=f"{trader_id.lower()}@traders.local",
                password=trader_password,
                role_name="trader",
                trader_ids=[trader_id],
            )
            for trader_id in trader_ids
        )
        created_analyst = ensure_user(
            session=session,
            email=ANALYST_EMAIL,
            password=analyst_password,
            role_name="analyst",
            trader_ids=trader_ids,
        )
        created_admin = ensure_user(
            session=session,
            email=ADMIN_EMAIL,
            password=admin_password,
            role_name="admin",
            trader_ids=trader_ids,
        )
        session.commit()

    print(f"Created trader users: {created_trader_users}")
    print(f"Created analyst user: {created_analyst}")
    print(f"Created admin user: {created_admin}")


if __name__ == "__main__":
    main()

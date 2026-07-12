"""PostgreSQL authentication repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from trader_intelligence_ai_copilot.auth.models import AuthenticatedUser, RefreshTokenRecord
from trader_intelligence_ai_copilot.database.models import RefreshTokenModel, TraderAccessModel, UserModel, UserRoleModel
from trader_intelligence_ai_copilot.repositories.auth_repository import AuthRepository


class PostgresAuthRepository(AuthRepository):
    """Read and write authentication records through SQLAlchemy ORM."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_user_by_email(self, email: str) -> AuthenticatedUser | None:
        user = self._session.scalar(select(UserModel).where(UserModel.email == email))
        return self._to_user(user) if user else None

    def get_user_by_id(self, user_id: UUID) -> AuthenticatedUser | None:
        user = self._session.get(UserModel, user_id)
        return self._to_user(user) if user else None

    def create_refresh_token(self, record: RefreshTokenRecord) -> None:
        self._session.add(RefreshTokenModel(id=record.id, user_id=record.user_id, token_hash=record.token_hash, expires_at=record.expires_at, revoked_at=record.revoked_at))
        self._session.commit()

    def get_refresh_token(self, token_hash: str) -> RefreshTokenRecord | None:
        token = self._session.scalar(select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash))
        if token is None:
            return None
        return RefreshTokenRecord(token.id, token.user_id, token.token_hash, token.expires_at, token.revoked_at)

    def revoke_refresh_token(self, token_id: UUID, revoked_at: datetime) -> None:
        token = self._session.get(RefreshTokenModel, token_id)
        if token is not None:
            token.revoked_at = revoked_at
            self._session.commit()

    def _to_user(self, user: UserModel) -> AuthenticatedUser:
        roles = self._session.scalars(select(UserRoleModel.role_name).where(UserRoleModel.user_id == user.id)).all()
        trader_ids = self._session.scalars(select(TraderAccessModel.trader_id).where(TraderAccessModel.user_id == user.id)).all()
        return AuthenticatedUser(user.id, user.email, user.password_hash, user.is_active, frozenset(roles), frozenset(trader_ids))

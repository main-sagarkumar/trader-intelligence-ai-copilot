"""Application service for local login and refresh-token rotation."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

from trader_intelligence_ai_copilot.auth import JWTService, PasswordService, RefreshTokenRecord, TokenPair
from trader_intelligence_ai_copilot.config.app.security import SecurityConfig
from trader_intelligence_ai_copilot.repositories.auth_repository import AuthRepository


class AuthenticationError(ValueError):
    """Raised when credentials or token state are not valid."""


class AuthService:
    """Authenticate users and rotate persisted refresh tokens."""

    def __init__(self, repository: AuthRepository, jwt_service: JWTService, security: SecurityConfig) -> None:
        self._repository = repository
        self._jwt_service = jwt_service
        self._security = security

    def login(self, email: str, password: str) -> TokenPair:
        user = self._repository.get_user_by_email(email)
        if user is None or not user.is_active or not PasswordService.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        return self._issue_pair(user)

    def refresh(self, refresh_token: str) -> TokenPair:
        claims = self._jwt_service.decode_refresh_token(refresh_token)
        token = self._repository.get_refresh_token(self._hash(refresh_token))
        if token is None or token.revoked_at is not None or token.expires_at <= datetime.now(UTC):
            raise AuthenticationError("Refresh token is invalid or revoked.")
        if str(token.id) != claims.get("jti"):
            raise AuthenticationError("Refresh token is invalid.")
        user = self._repository.get_user_by_id(UUID(str(claims["sub"])))
        if user is None or not user.is_active:
            raise AuthenticationError("User is inactive or unavailable.")
        self._repository.revoke_refresh_token(token.id, datetime.now(UTC))
        return self._issue_pair(user)

    def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token, ending its ability to create new sessions."""
        claims = self._jwt_service.decode_refresh_token(refresh_token)
        token = self._repository.get_refresh_token(self._hash(refresh_token))
        if token is None or str(token.id) != claims.get("jti"):
            raise AuthenticationError("Refresh token is invalid.")

        self._repository.revoke_refresh_token(token.id, datetime.now(UTC))

    def _issue_pair(self, user) -> TokenPair:
        token_id = uuid4()
        refresh_token = self._jwt_service.create_refresh_token(user.id, token_id)
        self._repository.create_refresh_token(RefreshTokenRecord(token_id, user.id, self._hash(refresh_token), datetime.now(UTC) + timedelta(days=self._security.refresh_token_expire_days), None))
        return TokenPair(self._jwt_service.create_access_token(user), refresh_token)

    @staticmethod
    def _hash(token: str) -> str:
        return sha256(token.encode()).hexdigest()

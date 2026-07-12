"""JWT creation and validation for application sessions."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from trader_intelligence_ai_copilot.auth.models import AuthenticatedUser
from trader_intelligence_ai_copilot.config.app.security import SecurityConfig


class InvalidTokenError(ValueError):
    """Raised when a token cannot be validated for its intended use."""


class JWTService:
    """Issue and validate signed access and refresh tokens."""

    def __init__(self, config: SecurityConfig) -> None:
        """Initialize the service from security configuration."""
        self._config = config
        self._secret_key = config.jwt_secret_key.get_secret_value()

        if not self._secret_key:
            raise ValueError("JWT_SECRET_KEY must be configured.")

    def create_access_token(self, user: AuthenticatedUser) -> str:
        """Create a short-lived access token containing effective roles."""
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self._config.access_token_expire_minutes
        )
        return self._encode(
            {
                "sub": str(user.id),
                "roles": sorted(user.roles),
                "token_type": "access",
                "exp": expires_at,
            }
        )

    def create_refresh_token(self, user_id: UUID, token_id: UUID) -> str:
        """Create a long-lived refresh token bound to a persisted token ID."""
        expires_at = datetime.now(UTC) + timedelta(
            days=self._config.refresh_token_expire_days
        )
        return self._encode(
            {
                "sub": str(user_id),
                "jti": str(token_id),
                "token_type": "refresh",
                "exp": expires_at,
            }
        )

    def decode_access_token(self, token: str) -> dict[str, object]:
        """Validate and decode an access token."""
        return self._decode(token, expected_type="access")

    def decode_refresh_token(self, token: str) -> dict[str, object]:
        """Validate and decode a refresh token."""
        return self._decode(token, expected_type="refresh")

    def _encode(self, claims: dict[str, object]) -> str:
        return jwt.encode(
            {
                **claims,
                "iss": self._config.jwt_issuer,
                "aud": self._config.jwt_audience,
            },
            self._secret_key,
            algorithm=self._config.algorithm,
        )

    def _decode(self, token: str, expected_type: str) -> dict[str, object]:
        try:
            claims = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._config.algorithm],
                issuer=self._config.jwt_issuer,
                audience=self._config.jwt_audience,
            )
        except JWTError as error:
            raise InvalidTokenError("Invalid or expired token.") from error

        if claims.get("token_type") != expected_type:
            raise InvalidTokenError("Token type is not valid for this operation.")

        return claims

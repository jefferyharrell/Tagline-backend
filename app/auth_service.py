"""
auth_service.py

Service layer for authentication: password verification, token issuance, validation, and revocation.
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional, Tuple

from jose import jwt

from app.config import Settings
from app.token_store import TokenStore


class AuthService:
    def __init__(self, settings: Settings, token_store: TokenStore):
        self.settings = settings
        self.token_store = token_store

    def verify_password(self, password: str) -> bool:
        """Check if the provided password matches the backend password."""
        return secrets.compare_digest(password, self.settings.BACKEND_PASSWORD or "")

    def refresh_tokens(self, refresh_token: str) -> Tuple[str, str, int, int]:
        """
        Exchange a valid refresh token for new access and refresh tokens.
        Revokes the used refresh token.
        Returns (access_token, refresh_token, access_expiry, refresh_expiry)
        Raises Exception if token is invalid, expired, or revoked.
        """
        # 1. Validate the refresh token
        claims = self.validate_token(refresh_token, token_type="refresh")
        if not claims:
            raise Exception("Invalid or expired refresh token")
        # 2. Revoke the used refresh token
        self.revoke_refresh_token(refresh_token)
        # 3. Issue new tokens
        return self.issue_tokens()

    def issue_tokens(self) -> Tuple[str, str, int, int]:
        """
        Issue a new access and refresh token pair.
        Ensures the refresh token is unique in the store.
        Returns (access_token, refresh_token, access_expiry, refresh_expiry)
        """
        now = datetime.now(UTC)
        access_exp = now + timedelta(seconds=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        refresh_exp = now + timedelta(
            seconds=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS
        )
        access_token = jwt.encode(
            {
                "exp": int(access_exp.timestamp()),
                "type": "access",
                "jti": secrets.token_hex(8),  # Add random JTI for uniqueness
            },
            str(self.settings.JWT_SECRET_KEY),
            algorithm="HS256",
        )
        # Guarantee a unique refresh token
        for _ in range(5):  # Try a few times before giving up
            refresh_token = jwt.encode(
                {
                    "exp": int(refresh_exp.timestamp()),
                    "type": "refresh",
                    "jti": secrets.token_hex(8),  # Add random JTI for uniqueness
                },
                str(self.settings.JWT_SECRET_KEY),
                algorithm="HS256",
            )
            # Try to store the token, fail if it already exists
            if not self.token_store.is_refresh_token_valid(refresh_token):
                try:
                    self.token_store.store_refresh_token(
                        refresh_token, self.settings.REFRESH_TOKEN_EXPIRE_SECONDS
                    )
                    break
                except Exception:
                    continue
        else:
            raise RuntimeError(
                "Could not generate a unique refresh token after several attempts."
            )
        return (
            access_token,
            refresh_token,
            self.settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            self.settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

    def validate_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """
        Validate a JWT and ensure it's not expired or revoked (for refresh tokens).
        Returns decoded claims if valid, else None.
        """
        try:
            payload = jwt.decode(
                token,
                str(self.settings.JWT_SECRET_KEY),
                algorithms=["HS256"],
            )
            if payload.get("type") != token_type:
                return None
            if token_type == "refresh":
                # Check if refresh token is revoked/expired in the token store
                if not self.token_store.is_refresh_token_valid(token):
                    return None
            return payload
        except Exception:
            return None

    def revoke_refresh_token(self, token: str) -> None:
        """
        Revoke a refresh token (by marking it revoked in the token store).
        This now matches the TokenStore interface (returns None).
        """
        try:
            self.token_store.revoke_refresh_token(token)
        except Exception:
            # Optionally log the exception here
            pass

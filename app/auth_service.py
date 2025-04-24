"""
auth_service.py

Service layer for authentication: password verification, token issuance, validation, and revocation.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional, Tuple

from jose import jwt
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import RefreshToken


class AuthService:
    def __init__(self, settings: Settings, db: Session):
        self.settings = settings
        self.db = db

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
        Ensures the refresh token is unique in the DB.
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
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            exists = self.db.query(RefreshToken).filter_by(token=token_hash).first()
            if not exists:
                break
        else:
            raise RuntimeError(
                "Could not generate a unique refresh token after several attempts."
            )
        db_token = RefreshToken(
            token=token_hash,
            issued_at=now,
            expires_at=refresh_exp,
            revoked=False,
        )
        self.db.add(db_token)
        self.db.commit()
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
                # Check if refresh token is revoked
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                db_token = (
                    self.db.query(RefreshToken).filter_by(token=token_hash).first()
                )
                if not db_token or db_token.revoked:
                    return None
            return payload
        except Exception:
            return None

    def revoke_refresh_token(self, token: str) -> bool:
        """
        Revoke a refresh token (by marking it revoked in DB).
        Returns True if successful, False otherwise.
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        db_token = self.db.query(RefreshToken).filter_by(token=token_hash).first()
        if db_token and not db_token.revoked:
            db_token.revoked = True
            db_token.revoked_at = datetime.now(UTC)
            self.db.commit()
            return True
        return False

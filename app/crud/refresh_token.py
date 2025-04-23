"""
CRUD repository for RefreshToken model.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import RefreshToken


class RefreshTokenRepository:
    """Repository for RefreshToken CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        token: str,
        expires_at: datetime,
        revoked: bool = False,
        revoked_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
    ) -> RefreshToken:
        """Create and persist a new RefreshToken."""
        refresh_token = RefreshToken(
            token=token,
            expires_at=expires_at,
            revoked=revoked,
            revoked_at=revoked_at,
            last_used_at=last_used_at,
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get(self, token_id: uuid.UUID) -> Optional[RefreshToken]:
        """Get a RefreshToken by its ID."""
        return self.db.get(RefreshToken, token_id)

    def list(self) -> List[RefreshToken]:
        """List all RefreshTokens."""
        return self.db.query(RefreshToken).all()

    def update(self, token_id: uuid.UUID, **kwargs) -> Optional[RefreshToken]:
        """Update a RefreshToken's fields."""
        token = self.get(token_id)
        if not token:
            return None
        for key, value in kwargs.items():
            if hasattr(token, key):
                setattr(token, key, value)
        self.db.commit()
        self.db.refresh(token)
        return token

    def delete(self, token_id: uuid.UUID) -> None:
        """Delete a RefreshToken by its ID."""
        token = self.get(token_id)
        if token:
            self.db.delete(token)
            self.db.commit()

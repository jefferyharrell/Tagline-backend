"""
token_store.py

Abstract base class for refresh token storage, and Redis-backed implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional


class TokenStore(ABC):
    """Abstract base class for refresh token storage backends."""

    @abstractmethod
    def store_refresh_token(self, token: str, expires_in: int) -> None:
        """Store a refresh token with a given TTL (seconds)."""
        pass

    @abstractmethod
    def is_refresh_token_valid(self, token: str) -> bool:
        """Return True if the token exists and is not revoked/expired."""
        pass

    @abstractmethod
    def revoke_refresh_token(self, token: str) -> None:
        """Revoke a refresh token (make it invalid for future use)."""
        pass

    @abstractmethod
    def get_refresh_token_metadata(self, token: str) -> Optional[dict]:
        """Return metadata for auditing/debug, or None if not found."""
        pass

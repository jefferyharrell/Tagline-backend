"""
token_store.py

Provides an in-memory implementation of the TokenStore for testing purposes.
"""

import logging
from typing import Dict, Optional

from tagline_backend_app.token_store import TokenStore

logger = logging.getLogger(__name__)


class InMemoryTokenStore(TokenStore):
    """A simple in-memory mock for the TokenStore focusing on refresh tokens."""

    def __init__(self):
        # Store refresh tokens, value can indicate validity (e.g., True)
        self._refresh_tokens: Dict[str, bool] = {}
        logger.debug("InMemoryTokenStore initialized.")

    def store_refresh_token(self, token: str, expires_in: int) -> None:
        """Mock storing a refresh token."""
        logger.debug(
            f"InMemoryTokenStore: Storing token {token[:5]}... (expiry: {expires_in}s)"
        )
        self._refresh_tokens[token] = True  # Mark as valid

    def is_refresh_token_valid(self, token: str) -> bool:
        """Mock checking if a refresh token is valid (exists in store)."""
        is_valid = self._refresh_tokens.get(token, False)
        logger.debug(
            f"InMemoryTokenStore: Checking token {token[:5]}... -> Valid: {is_valid}"
        )
        return is_valid

    def revoke_refresh_token(self, token: str) -> None:
        """Mock revoking a refresh token (removing it from store)."""
        logger.debug(f"InMemoryTokenStore: Revoking token {token[:5]}...")
        if token in self._refresh_tokens:
            del self._refresh_tokens[token]

    def get_refresh_token_metadata(self, token: str) -> Optional[dict]:
        """Mock getting metadata (returns simple status if valid)."""
        is_valid = self.is_refresh_token_valid(token)
        logger.debug(
            f"InMemoryTokenStore: Getting metadata for token {token[:5]}... -> Valid: {is_valid}"
        )
        if is_valid:
            return {"status": "valid", "revoked": False}  # Minimal metadata
        return None

    def clear(self):
        """Helper method to clear the store for testing."""
        logger.debug("InMemoryTokenStore: Clearing all tokens.")
        self._refresh_tokens.clear()

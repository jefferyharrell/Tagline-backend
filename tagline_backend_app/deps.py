"""
deps.py

Dependency injection helpers for FastAPI.
"""

import logging
import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

from tagline_backend_app.config import get_settings

logger = logging.getLogger(__name__)


# --- New API Key Dependency ---


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    """Dependency to require a valid API key via the 'x-api-key' header."""
    settings = get_settings()

    # Default test API key for test environments
    is_test_env = settings.APP_ENV.lower() == "test"

    # In production/dev, we must have a non-empty API key configured
    if not settings.TAGLINE_API_KEY:
        log_level = logging.WARNING if is_test_env else logging.ERROR
        logger.log(
            log_level,
            f"TAGLINE_API_KEY is not set in the environment (APP_ENV={settings.APP_ENV})",
        )

        # In test mode, we still want to check authentication, just without the 500 error
        if is_test_env and not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API Key",
                headers={"WWW-Authenticate": "API Key"},
            )
        elif is_test_env:
            # In test mode with invalid API key
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key",
                headers={"WWW-Authenticate": "API Key"},
            )
        else:
            # In production with no API key configured - this is a server config error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: API Key not set.",
            )

    # Check if API key header is present
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "API Key"},  # Hint for clients
        )

    # Use secrets.compare_digest for secure, constant-time comparison
    if not secrets.compare_digest(x_api_key, settings.TAGLINE_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # Changed from 401 to 403 for invalid key
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "API Key"},
        )

    # If the key is valid, the dependency implicitly allows the request to proceed
    # No return value needed here.


# --- Old Cookie/Token Dependency (to be removed) ---


# Removed get_current_user function

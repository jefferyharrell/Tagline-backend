import logging
import os
from pathlib import Path
from typing import Dict, Optional

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from tagline_backend_app.config import Settings

# Local application imports
from tagline_backend_app.deps import get_token_store
from tagline_backend_app.main import create_app
from tagline_backend_app.token_store import TokenStore

# Determine project root for .env loading
project_root = Path(__file__).parent.parent.parent

# Override Redis URL for integration tests (local) - We keep this but won't use it
os.environ["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
# Force in-memory SQLite DB for integration tests
os.environ["DB_URL"] = "sqlite:///:memory:"

# Load environment variables from .env file using pathlib
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


# --- Mock Token Store --- #

logger = logging.getLogger(__name__)


class MockTokenStore(TokenStore):
    """A simple in-memory mock for the TokenStore focusing on refresh tokens."""

    def __init__(self):
        # Store refresh tokens, value can indicate validity (e.g., True)
        self._refresh_tokens: Dict[str, bool] = {}

    def store_refresh_token(self, token: str, expires_in: int) -> None:
        """Mock storing a refresh token."""
        # logger.debug(f"MOCK: Storing refresh token {token[:5]}... with expiry {expires_in}s")
        self._refresh_tokens[token] = True  # Mark as valid

    def is_refresh_token_valid(self, token: str) -> bool:
        """Mock checking if a refresh token is valid (exists in store)."""
        # logger.debug(f"MOCK: Checking validity for refresh token {token[:5]}...")
        return self._refresh_tokens.get(token, False)

    def revoke_refresh_token(self, token: str) -> None:
        """Mock revoking a refresh token (removing it from store)."""
        # logger.debug(f"MOCK: Revoking refresh token {token[:5]}...")
        if token in self._refresh_tokens:
            del self._refresh_tokens[token]

    def get_refresh_token_metadata(self, token: str) -> Optional[dict]:
        """Mock getting metadata (returns simple status if valid)."""
        # logger.debug(f"MOCK: Getting metadata for refresh token {token[:5]}...")
        if self.is_refresh_token_valid(token):
            return {"status": "valid"}  # Minimal metadata
        return None


@pytest.fixture(scope="session")
def mock_token_store():
    """Pytest fixture that provides a MockTokenStore instance."""
    # Using session scope ensures the same instance is used across all tests
    instance = MockTokenStore()
    logger.debug(f"CONFTEST: mock_token_store fixture created: {instance}")
    return instance


# --- Test Client Fixture --- #


@pytest.fixture(scope="session")
def test_client(mock_token_store):
    logger.debug("CONFTEST: test_client fixture starting.")

    # --- Key change: Create explicit test settings ---
    # Load defaults, but force APP_ENV to 'test'
    # We might need to load other essential keys if .env isn't read
    # automatically in this context (e.g., JWT_SECRET_KEY)
    test_settings = Settings(
        APP_ENV="test",
        # Load others from env or set defaults if needed
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "default-test-secret"),
        BACKEND_PASSWORD=os.getenv("BACKEND_PASSWORD", "default-test-password"),
        DATABASE_URL=os.getenv(
            "DATABASE_URL_TEST", "sqlite+pysqlite:///:memory:"
        ),  # Use test DB URL
        REDIS_URL=os.getenv("REDIS_URL", "redis://mock-redis:6379/0"),  # Mock Redis URL
        # Add other necessary settings explicitly if tests fail later
    )
    logger.debug(
        f"CONFTEST: Created test_settings with APP_ENV='{test_settings.APP_ENV}'"
    )

    # Create the app using the specific test settings
    app = create_app(settings=test_settings)
    logger.debug("CONFTEST: FastAPI app created using test_settings.")

    # Override the token store in app state
    app.state.token_store = mock_token_store
    logger.debug(f"CONFTEST: Overrode app.state.token_store with: {mock_token_store}")

    # Most importantly: Override the get_token_store DEPENDENCY
    # This ensures route handlers receive our mock, not a new RedisTokenStore
    app.dependency_overrides[get_token_store] = lambda: mock_token_store
    logger.debug(
        f"CONFTEST: Set dependency override for get_token_store to use {mock_token_store}"
    )

    # Create the test client
    client = TestClient(app)
    with client:
        yield client

    # Cleanup overrides after tests are done
    app.dependency_overrides = {}
    logger.debug("CONFTEST: Cleared dependency overrides.")

import logging
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from tagline_backend_app.config import Settings, clear_settings_cache, get_settings
from tagline_backend_app.main import create_app

# Determine project root for .env loading
project_root = Path(__file__).parent.parent.parent


# Force in-memory SQLite DB for integration tests
os.environ["DB_URL"] = "sqlite:///:memory:"

# Load environment variables from .env file using pathlib
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


logger = logging.getLogger(__name__)


# --- Test Client Fixture --- #


@pytest.fixture(scope="session")
def test_client():
    logger.debug("CONFTEST: test_client fixture starting.")

    # Set APP_ENV to test *before* creating Settings
    # (ensure it's set if not already by e.g. .env file)
    original_app_env = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "test"

    # Create Settings instance; __init__ should handle test defaults now
    test_settings = Settings()
    logger.debug(
        f"CONFTEST: Created test_settings. APP_ENV='{test_settings.APP_ENV}', "
        f"API_KEY='{test_settings.TAGLINE_API_KEY}'"  # Log to verify
    )

    # Restore original APP_ENV if it existed
    if original_app_env is None:
        del os.environ["APP_ENV"]
    else:
        os.environ["APP_ENV"] = original_app_env

    # Create the app using the specific test settings
    app = create_app(settings=test_settings)
    logger.debug("CONFTEST: FastAPI app created using test_settings.")

    # --- Key change: Override get_settings dependency ---
    # Ensure that dependency injection uses *our* test_settings
    def override_get_settings():
        return test_settings

    # --- Key change: Clear cache before overriding ---
    clear_settings_cache()
    app.dependency_overrides[get_settings] = override_get_settings
    logger.debug(
        "CONFTEST: Cleared settings cache and overrode get_settings dependency."
    )

    # Yield the test client
    with TestClient(app) as client:
        yield client

    # Clean up dependency override after tests are done
    app.dependency_overrides.clear()
    clear_settings_cache()  # Clear cache again on teardown just in case
    logger.debug("CONFTEST: Cleared dependency overrides and settings cache.")

    logger.debug("CONFTEST: Test client fixture finished.")

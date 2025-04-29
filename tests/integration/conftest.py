import logging
import os
from pathlib import Path

import psycopg2
import pytest
from dotenv import load_dotenv

# Determine project root for .env loading
project_root = Path(__file__).parent.parent.parent

# Load environment variables from .env file using pathlib
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# --- Test Client Fixture --- #


@pytest.fixture(scope="session")
def test_client():
    logger.debug("CONFTEST: test_client fixture starting.")

    # Set test DB environment and bust caches *after* .env is loaded, before settings/app/engine
    original_app_env = os.environ.get("APP_ENV")

    os.environ["APP_ENV"] = "test"
    # Force in-memory storage for integration tests to avoid hitting live services (e.g., Dropbox)
    original_storage_provider = os.environ.get("STORAGE_PROVIDER")
    os.environ["STORAGE_PROVIDER"] = "memory"
    # Use TEST_DATABASE_URL for all integration tests
    test_db_url = (
        os.environ.get("TEST_DATABASE_URL")
        or "postgresql://tagline:tagline@localhost:5432/tagline_test"
    )
    os.environ["DATABASE_URL"] = test_db_url

    # --- Drop and recreate the test DB before running tests ---
    admin_url = test_db_url.replace("/tagline_test", "/postgres")
    admin_conn = psycopg2.connect(admin_url)
    admin_conn.autocommit = True
    with admin_conn.cursor() as cur:
        # Terminate all other connections to the test DB
        cur.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'tagline_test' AND pid <> pg_backend_pid();"
        )
        cur.execute("DROP DATABASE IF EXISTS tagline_test;")
        cur.execute("CREATE DATABASE tagline_test;")
    admin_conn.close()

    # --- Run migrations (alembic) to set up schema ---
    # (Assumes alembic.ini is configured to use DATABASE_URL)
    import subprocess

    subprocess.run(["alembic", "upgrade", "head"], check=True)

    # Import all DB/app modules *inside* the fixture to avoid premature cache population
    from tagline_backend_app.config import Settings, clear_settings_cache, get_settings
    from tagline_backend_app.db import get_engine, get_session_local
    from tagline_backend_app.main import create_app

    get_engine.cache_clear()
    get_session_local.cache_clear()
    clear_settings_cache()

    # Create Settings instance; __init__ should handle test defaults now
    test_settings = Settings()
    logger.debug(
        f"CONFTEST: Created test_settings. APP_ENV='{test_settings.APP_ENV}', "
        f"API_KEY='{test_settings.TAGLINE_API_KEY}'"  # Log to verify
    )

    # Create the app using the specific test settings (app factory will create tables in test env)
    app = create_app(settings=test_settings)
    logger.debug("CONFTEST: FastAPI app created using test_settings.")

    # Restore original APP_ENV if it existed
    if original_app_env is None:
        del os.environ["APP_ENV"]
    else:
        os.environ["APP_ENV"] = original_app_env
    # Restore STORAGE_PROVIDER
    if original_storage_provider is None:
        del os.environ["STORAGE_PROVIDER"]
    else:
        os.environ["STORAGE_PROVIDER"] = original_storage_provider

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
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client

    # Clean up dependency override after tests are done
    app.dependency_overrides.clear()
    clear_settings_cache()  # Clear cache again on teardown just in case
    logger.debug("CONFTEST: Cleared dependency overrides and settings cache.")

    logger.debug("CONFTEST: Test client fixture finished.")

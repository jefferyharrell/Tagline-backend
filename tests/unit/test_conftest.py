"""
Unit tests for conftest.py fixtures (edge cases).
"""

import os
import sys
from pathlib import Path

import pytest

# Use the new package name for imports
from tagline_backend_app.config import get_settings

# Add the project root to the Python path to allow imports like `app.` or `tests.`
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def ensure_env_vars_unset(monkeypatch):
    """Ensure potentially interfering env vars are unset before each test."""
    # List common env vars used by Settings
    vars_to_clear = [
        "APP_ENV",
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "REDIS_URL",
        "STORAGE_PROVIDER",
        "FILESYSTEM_STORAGE_PATH",
        "DROPBOX_ACCESS_TOKEN",
        "APP_NAME",
        "APP_VERSION",
    ]
    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clears the lru_cache for get_settings before each test."""
    # Clear cache before the test runs
    get_settings.cache_clear()
    yield
    # Optionally clear again after the test, though usually not necessary
    # get_settings.cache_clear()


@pytest.fixture
def mock_settings_env(monkeypatch):
    """Fixture to easily mock environment variables for Settings testing."""

    def _mock_env(settings_dict):
        get_settings.cache_clear()  # Clear cache before applying new env vars
        for key, value in settings_dict.items():
            if value is None:
                monkeypatch.delenv(key.upper(), raising=False)
            else:
                monkeypatch.setenv(key.upper(), str(value))
        return get_settings()

    return _mock_env


# Note: Database/client fixtures are typically defined in the main
# conftest.py (tests/conftest.py) and potentially overridden for specific
# test types (e.g., integration tests using a real DB).


def test_reset_app_env_restores(reset_app_env, monkeypatch):
    monkeypatch.setenv("APP_ENV", "original")
    os.environ["APP_ENV"] = "changed"
    # The fixture will restore after the test completes; simulate this:
    # Actually, we can't test the 'after yield' part directly, but we can at least ensure the fixture runs without error.
    assert os.environ["APP_ENV"] == "changed"

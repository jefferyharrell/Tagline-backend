"""
Shared pytest fixtures and configuration for Tagline backend tests.
- Ensures app package is importable (fixes sys.path).
- Provides a reusable TestClient fixture.
- Manages APP_ENV environment variable for test isolation.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure Tagline-backend is on sys.path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Reusable FastAPI TestClient for the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_app_env():
    """Reset APP_ENV after each test to avoid cross-test contamination."""
    original = os.environ.get("APP_ENV")
    yield
    if original is not None:
        os.environ["APP_ENV"] = original
    else:
        os.environ.pop("APP_ENV", None)

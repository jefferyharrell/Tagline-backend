# conftest.py for Tagline backend tests
# Ensures DATABASE_URL is always set for all test runs (unit, integration, e2e)
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# You can add global pytest fixtures below as needed.

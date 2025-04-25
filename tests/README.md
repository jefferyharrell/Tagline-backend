# Tagline Backend Testing Guide

## Overview

This directory contains all unit, integration, and end-to-end (e2e) tests for the Tagline backend. We use `pytest` for all testing, with FastAPI, SQLAlchemy, and a variety of storage providers and test fixtures.

---

## SQLite, SQLAlchemy, and Integration Tests: The "No Such Table" Saga

### The Problem

When using SQLite as a test database with SQLAlchemy and FastAPI, you may encounter mysterious errors like:

```
(sqlite3.OperationalError) no such table: photos
```

This usually happens in integration tests that spin up a real FastAPI app and hit endpoints that access the database. Even if you create the tables in your test fixture, the app may not see them—because SQLAlchemy's engine/session caching and SQLite's in-memory quirks mean you can easily end up with two separate databases in the same process.

### The Root Cause

- **SQLAlchemy's `@lru_cache`**: Our `get_engine()` and `get_session_local()` functions are cached. If they're called before your test fixture sets up the schema, the resulting engine/sessionmaker are locked in for the app's lifetime.
- **SQLite in-memory DBs**: Each new connection to an in-memory SQLite DB is isolated. Even with URI tricks, if SQLAlchemy creates a new engine or session, you get a separate, empty database.

### The Solution

**Control the order of operations in your test fixture:**

1. Set all environment variables (`DATABASE_URL`, etc.) for your test DB.
2. Clear the `lru_cache` on `get_engine` and `get_session_local` to force SQLAlchemy to pick up the new settings.
3. Create the engine and the tables.
4. Patch the global DB accessors for extra safety.
5. Only then, instantiate your FastAPI app.

This ensures that every part of your stack—tests, app, and dependencies—uses the same database connection and sees the same schema.

#### Example Fixture Pattern

```python
@pytest.fixture
def integration_app(tmp_path_factory):
    import os
    import app.db as app_db
    from app.db import get_engine, get_session_local
    from sqlalchemy.orm import sessionmaker
    from app.models import Base

    tmp_path = tmp_path_factory.mktemp("db")
    db_url = f"sqlite:///{tmp_path}/test_db.sqlite3"
    os.environ["DATABASE_URL"] = db_url
    os.environ["STORAGE_PROVIDER"] = "memory"

    # Bust caches to ensure fresh engine/session
    get_engine.cache_clear()
    get_session_local.cache_clear()

    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    # Patch global accessors (extra safety)
    app_db.get_engine = lambda: engine
    app_db.get_session_local = lambda: SessionLocal

    from app.main import create_app
    app = create_app()
    # ... inject any test providers, etc ...
    return app
```

### TL;DR
- Always clear the engine/session lru_cache after setting test env vars.
- Use a file-based SQLite DB for integration tests, not in-memory.
- Create tables before instantiating the app.
- Patch global DB accessors if needed.

This will save you and your teammates from hours of "why does my test DB have no tables?!" pain. Happy testing!

---

## Other Testing Notes

- Unit tests live in `tests/unit/`, integration tests in `tests/integration/`, and e2e tests in `tests/e2e/`.
- Integration tests are marked with `@pytest.mark.integration`.
- See the `Justfile` for recipes to run each type of test.

For more details, see the main project `README.md` or ask your friendly neighborhood AI assistant (that’s me!).

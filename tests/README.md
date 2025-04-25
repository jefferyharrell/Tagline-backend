# Tagline Backend Testing Guide

## Overview

This directory contains all unit, integration, and end-to-end (e2e) tests for the Tagline backend. We use `pytest` for all testing, with FastAPI, SQLAlchemy, and a variety of storage providers and test fixtures.

---

## Testing Methodology

We organize our tests into three categories, each with a different philosophy and environment:

### 1. Unit Tests
- **Goal:** Test a single unit of code in isolation (e.g., a function, method, or class).
- **Mocking:** Everything external is mocked—databases, storage, network calls, etc.
- **Environment:** Runs fast, requires no backend server or real dependencies.
- **Typical location:** `tests/unit/`

### 2. Integration Tests
- **Goal:** Test interactions between multiple components (e.g., API + DB + storage), but still within a controlled Python process.
- **Mocking:** Minimal. Real implementations are used for most dependencies, but some external services may still be mocked.
- **Environment:** Uses FastAPI's `TestClient` to exercise real code paths, but does not require a running backend server or Docker.
- **Typical location:** `tests/integration/`

#### Storage Provider Configuration in Integration Tests

By default, Tagline's backend selects its storage provider (filesystem, memory, dropbox, etc.) based on the `STORAGE_PROVIDER` environment variable. For integration tests, you almost always want to use the in-memory provider for speed, isolation, and to avoid filesystem side effects.

**How to do it:**
- Use `monkeypatch.setenv("STORAGE_PROVIDER", "memory")` in your test or fixture _before_ creating the FastAPI app.
- This ensures all storage operations are ephemeral and test-isolated.

**Example:**
```python
@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "memory")
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)
```
This pattern is used in integration tests for endpoints like PATCH `/photos/{id}/metadata`, ensuring that both the database and storage layer are isolated and reproducible for each test run.

### 3. End-to-End (E2E) Tests
- **Goal:** Test the system as a whole, as a user would interact with it.
- **Mocking:** None. Requires a real backend server running (usually via Docker Compose), configured with the actual storage provider, database, etc.
- **Environment:** Interacts with the running server over HTTP, simulating real-world usage. May require setup/teardown of test data.
- **Typical location:** `tests/e2e/`

**Note for LLMs and humans:**
- Always choose the right test type for your goal. Unit tests are fast and focused, integration tests cover real component boundaries, and E2E tests verify the full stack in a production-like setup.
- E2E tests will fail if the backend server isn't running or is misconfigured. Unit/integration tests should never depend on external services.

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

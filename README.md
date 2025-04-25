# Tagline Backend

This directory contains the FastAPI backend for the Tagline photo management application.

> **Note:** Architectural decisions (like config, libraries, etc.) are documented in [docs/adr/](docs/adr/).

## Setup

### Environment Variables

The backend is configured using environment variables, which can be set in a `.env` file at the project root (see `.env.example`).

- `DATABASE_URL`: Database connection string. If not set, defaults to `sqlite:///./tagline.db` (a local SQLite file in the backend directory).
    - Example for SQLite (default): `sqlite:///./tagline.db`
    - Example for Postgres: `postgresql+psycopg2://user:password@localhost:5432/tagline`

- `STORAGE_PROVIDER`: Selects the storage backend. Options:
    - `filesystem`: Real file storage (default; requires `FILESYSTEM_STORAGE_PATH`)
    - `null`: Accepts all ops, stores nothing, never fails (ideal for CI/demo)
    - `memory`: Ephemeral in-memory storage, wiped on restart (ideal for tests/dev)
    - `dropbox`: Dropbox via official SDK (refresh token flow; production-ready)

- `FILESYSTEM_STORAGE_PATH`: Absolute path to the directory where files will be stored (required only for `filesystem` provider).
- `DROPBOX_REFRESH_TOKEN`: Dropbox OAuth2 refresh token (required; see below).
- `DROPBOX_APP_KEY`: Dropbox app key (required).
- `DROPBOX_APP_SECRET`: Dropbox app secret (required).
- `DROPBOX_ROOT_PATH`: Root path in Dropbox (all keys are relative to this path).
- `BACKEND_PASSWORD`: Password for backend authentication (required; keep this secret!).
- `JWT_SECRET_KEY`: Secret key for signing JWT tokens (required; must be long, random, and kept secret!).
- `DROPBOX_ACCESS_TOKEN`: [DEPRECATED] Legacy long-lived access token (not recommended; use refresh token flow instead).

**Provider config is now validated at runtime, not startup.**
- The app will start even if FILESYSTEM_STORAGE_PATH is unset, but endpoints that require the storage provider will return a clear error if misconfigured.
- Use the `/smoke-test` endpoint to check provider config health.

**Example values:**
```env
BACKEND_PASSWORD=your-backend-password-here
JWT_SECRET_KEY=superlongrandomstringforjwt
STORAGE_PROVIDER=filesystem
FILESYSTEM_STORAGE_PATH=/absolute/path/to/photo/storage
DROPBOX_REFRESH_TOKEN=your-dropbox-refresh-token-here
DROPBOX_APP_KEY=your-dropbox-app-key-here
DROPBOX_APP_SECRET=your-dropbox-app-secret-here
DROPBOX_ROOT_PATH=/dropbox_storage
```

### Redis Token Store & REDIS_URL

The backend uses Redis for authentication token storage (see ADR 0004).

- In development, Docker Compose provides a Redis service. Set `REDIS_URL=redis://redis:6379/0` in your `.env` file (see `.env.example`).
- In production, set `REDIS_URL` to your managed Redis instance (e.g., AWS ElastiCache, Upstash).
- The backend will refuse to start if `REDIS_URL` is not set.

See `.env.example` for sample configuration.

> **Security Note:** Never check real secrets into version control. Generate a strong, random JWT_SECRET_KEY for production (see README for tips).

You can copy `.env.example` to `.env` and edit as needed.

---

## Testing & Integration Test Setup

For detailed instructions, troubleshooting tips, and gotchas about running unit, integration, and e2e tests—including how to set up SQLite and SQLAlchemy for reliable integration tests—see [tests/README.md](tests/README.md).

## Extending Photo Storage Providers (For Developers)

To add a new storage backend:

1. **Implement the interface:**
   - Subclass `PhotoStorageProvider` (see `app/storage/provider.py`).
   - Implement all required methods: `list`, `retrieve`, and optionally `upload`, `delete`, `get_url`.
2. **Add provider settings:**
   - Create a Pydantic settings class for your provider in `app/config.py`.
   - Add any required environment variables to `.env.example` and document them in the README.
3. **Register the provider in `main.py`:**
   - Update the provider selection logic in `create_app()` to instantiate your provider when `STORAGE_PROVIDER` matches your backend.
4. **Test your provider:**
   - Add unit and (eventually) integration tests in `tests/unit/` or `tests/integration/` as appropriate.

See the existing `FilesystemPhotoStorageProvider` and `DropboxStorageProvider` for examples.

---

1.  Ensure you have Python 3.12+ installed.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4.  See [docs/database_setup.md](docs/database_setup.md) for full instructions on configuring and running the database.
5.  Install dependencies: `pip install -r requirements.txt`

## Running the Development Server

Use `uvicorn` to run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

## Running with Docker

You can build and run the backend in a Docker container:

### Build the image

```bash
docker build -t tagline-backend .
```

### Run the container

```bash
docker run --env-file .env -p 8000:8000 tagline-backend
```

- The API will be available at [http://localhost:8000](http://localhost:8000).
- Make sure to provide a `.env` file if your application needs environment variables.

---

## Running with Docker Compose

You can spin up the backend (and, in the future, the entire stack) using Docker Compose from the project root:

```bash
docker compose up --build
```

- The backend will be available at [http://localhost:8000](http://localhost:8000).
- To shut everything down, use:

```bash
docker compose down
```

When the frontend is added, it will also be available through Compose.

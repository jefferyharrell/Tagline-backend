# Database Setup for Tagline Backend

This guide explains how to configure, initialize, and manage the database for the Tagline backend.

## Supported Databases
- **SQLite** (for local development/testing)
- **PostgreSQL** (for production or advanced local setups)

**IMPORTANT: `DATABASE_URL` is now required for all environments. There is no default!**

### Setting DATABASE_URL

- **Local dev/test (in-memory SQLite):**
  - `DATABASE_URL=sqlite:///:memory:`
- **Local dev (file-based SQLite):**
  - `DATABASE_URL=sqlite:///./tagline.db`
- **Production (Postgres example):**
  - `DATABASE_URL=postgresql://user:password@localhost:5432/tagline`

### Troubleshooting

If you see an error like:

    RuntimeError: DATABASE_URL environment variable is required but not set. Please set it in your environment or .env file.

You must set `DATABASE_URL` in your environment or `.env` file before running the backend.

## Quick Start (Development)

1. **Clone the repository and set up your virtual environment:**
    ```sh
    git clone https://github.com/jefferyharrell/tagline-backend.git
    cd tagline-backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Configure your database connection:**
    - By default, Tagline uses SQLite and stores data in `./tagline.db`.
    - To use another database (e.g., PostgreSQL), set the `DATABASE_URL` environment variable:
      ```sh
      export DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/tagline
      ```
    - Example `.env` entry:
      ```env
      DATABASE_URL=sqlite:///./tagline.db
      ```

3. **Run migrations:**
    ```sh
    alembic upgrade head
    ```
    This creates all tables as defined in the latest models.

4. **Run the Server:**
    Start the FastAPI development server:
    ```bash
    uvicorn tagline_backend_app.main:app --reload
    ```
    FastAPI should now connect to your database using the URL specified in `.env` (or the default SQLite DB if `.env` or `DATABASE_URL` is not set).

## Environment Variables
- `DATABASE_URL` (optional): SQLAlchemy connection string. If not set, defaults to `sqlite:///./tagline.db`.
- `APP_ENV`: Set to `development`, `production`, or `test` as appropriate.

## SQLite Notes
- For most development, the default SQLite file is fine.
- For tests, an in-memory SQLite database is used automatically.
- If running with SQLite in production, beware of concurrency and file-locking limitations.

## Running Tests
- Tests use an in-memory SQLite DB for isolation and speed.
- No manual DB setup is required for running tests.

## Migrations
- Alembic is used for migrations.
- Migration scripts are in `alembic/`.
- Typical commands:
    - `alembic revision --autogenerate -m "Describe change"`
    - `alembic upgrade head`

## Troubleshooting
- If you change models and get errors, make sure to generate and apply a new migration.
- If `DATABASE_URL` is invalid or unreachable, the app will fail to start.
- For SQLite, ensure the app has write permissions to the target directory.

## See Also
- `.env.example` for sample environment variables.
- `tagline_backend_app/config.py` and `tagline_backend_app/db.py` for DB connection logic.
- [SQLAlchemy docs](https://docs.sqlalchemy.org/) for connection string formats and advanced usage.

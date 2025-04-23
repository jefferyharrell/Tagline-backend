# Tagline Backend

This directory contains the FastAPI backend for the Tagline photo management application.

> **Note:** Architectural decisions (like config, libraries, etc.) are documented in [docs/adr/](docs/adr/).

## Setup

### Environment Variables

The backend is configured using environment variables, which can be set in a `.env` file at the project root (see `.env.example`).

- `DATABASE_URL`: Database connection string. If not set, defaults to `sqlite:///./tagline.db` (a local SQLite file in the backend directory).
    - Example for SQLite (default): `sqlite:///./tagline.db`
    - Example for Postgres: `postgresql+psycopg2://user:password@localhost:5432/tagline`

- `STORAGE_PROVIDER`: Selects the storage backend. Default is `filesystem`.
- `FILESYSTEM_PHOTO_STORAGE_PATH`: (Required if using the filesystem provider) Absolute path to the directory where photos will be stored.
- `DROPBOX_ACCESS_TOKEN`: Access token for Dropbox API (**not yet implemented**).
- `DROPBOX_ROOT_PATH`: Root path in Dropbox (**not yet implemented**).

**Example .env snippet:**
```env
STORAGE_PROVIDER=filesystem
FILESYSTEM_PHOTO_STORAGE_PATH=/absolute/path/to/photo/storage
```

You can copy `.env.example` to `.env` and edit as needed.

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

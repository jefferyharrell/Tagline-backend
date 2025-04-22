# Tagline Backend

This directory contains the FastAPI backend for the Tagline photo management application.

## Setup

1.  Ensure you have Python 3.12+ installed.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4.  Install dependencies: `pip install -r requirements.txt`

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

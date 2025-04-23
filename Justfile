# Justfile for Tagline Backend
# Your one-stop CLI for all the commands you never want to memorize again.
# Usage: just <recipe>

# Show all available commands
default:
    just help

# Formatting and linting
format:
    # Auto-format code with black, isort, and fix trailing whitespace
    black .
    isort .
    ruff check --fix .

lint:
    pyright

# Testing
pytest:
    # Run all Python tests
    pytest

test: pytest

# Pre-Commit
pre-commit:
    # Run the pre-commit hoook
    pre-commit run --all-files

# Docker Compose
up:
    # Start all containers in the background
    docker compose up -d

down:
    # Stop all containers
    docker compose down

build:
    # Build Docker images
    docker compose build

logs:
    # Tail backend logs
    docker compose logs -f backend

shell:
    # Open a bash shell in the backend container
    docker exec -it tagline-backend-dev /bin/bash

# Alembic migrations (inside Docker)
migrate:
    # Apply all migrations in the backend container
    docker exec -it tagline-backend-dev alembic upgrade head

makemigration MESSAGE="Describe your migration":
    # Create a new Alembic migration (autogenerate) in Docker
    docker exec -it tagline-backend-dev alembic revision --autogenerate -m "{{MESSAGE}}"

dbshell:
    # Open a SQLite shell on the persistent DB in Docker
    docker exec -it tagline-backend-dev sqlite3 /data/tagline.db

# Clean up
prune:
    # Remove stopped containers, unused networks, dangling images/volumes
    docker system prune -f

# Show help
help:
    @echo "\nJustfile: Tagline Backend Project Helper\n"
    @just --list
    @echo "\nRun 'just <command>' to execute a task."
    @echo "For details: see docs/alembic-workflow.md and README.md."

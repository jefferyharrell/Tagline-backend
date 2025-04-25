# Justfile for Tagline Backend
# Your one-stop CLI for all the commands you never want to memorize again.
# Usage: just <recipe>

# Show all available commands
default:
    just help

# Set up dev environment
setup:
    #!/usr/bin/env bash
    if [ ! -d "venv" ]; then python -m venv venv; fi
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    if [ ! -f ".env" ]; then cp .env.example .env; fi
    echo -e "\033[1;32mSetup complete! Activate your venv with 'source venv/bin/activate' and start coding.\033[0m"

# Formatting and linting
format:
    # Auto-format code with black, isort, and fix trailing whitespace
    source venv/bin/activate && isort .
    source venv/bin/activate && black .

lint:
    source venv/bin/activate && ruff check --fix .
    source venv/bin/activate && pyright

# Testing
unit-tests:
    source venv/bin/activate && pytest --cov=app --cov-report=term-missing

e2e-tests:
    # Start backend containers and run end-to-end tests (pytest -m e2e)
    just up
    for i in {1..30}; do \
      if curl -s http://localhost:8000/ > /dev/null; then \
        echo "Backend is up!"; \
        break; \
      fi; \
      echo "Waiting for backend to be ready... ($$i)"; \
      sleep 1; \
    done
    source venv/bin/activate && pytest -m e2e
    echo -e '\033[1;36mE2E tests complete!\033[0m'

all:
    just format
    just lint
    just unit-tests
    just e2e-tests
    just pre-commit

# Remove Python cache files, test artifacts, and __pycache__ dirs
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    rm -rf .pytest_cache .mypy_cache .coverage coverage.xml
    echo "Cleaned up Python and test artifacts."

# Stop everything, rebuild images, and start fresh
rebuild:
    just down
    docker compose build --no-cache
    just up
    echo "Rebuilt and started fresh containers."

# Destroy and recreate the dev/test DB (fresh start)
reset-db:
    just down
    docker volume rm tagline-backend_tagline-db-data || true
    just up
    just migrate
    echo "Database reset and migrations applied."

# Upgrade all pip packages in requirements-dev.txt
update-deps:
    source venv/bin/activate
    pip install --upgrade -r requirements-dev.txt
    pip list --outdated
    echo "Dependencies updated. Check above for anything still out-of-date."

# Pre-Commit
pre-commit:
    # Run the pre-commit hoook
    source venv/bin/activate && pre-commit run --all-files

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

# Connect to the Redis shell in the dev container
redis-shell:
	docker exec -it tagline-redis-dev redis-cli

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

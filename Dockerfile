# Use an official Python runtime as a parent image
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for Pillow or other C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

# Install Poetry (if you use it - adjust if using pip directly)
# RUN pip install poetry
# COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# --- If using requirements.txt directly ---
# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt
# -------

# --- Stage 2: Final image ---
FROM python:3.12-slim

WORKDIR /app

# Copy installed wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install packages from wheels
RUN pip install --no-cache /wheels/*

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application (adjust if your entrypoint is different)
# For development with live reload (matches docker-compose.yml command):
CMD ["uvicorn", "tagline_backend_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# For production (usually without reload):
# CMD ["uvicorn", "tagline_backend_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

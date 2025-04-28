# Tagline Backend Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install system dependencies and HEIC/HEIF support
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    libheif1 \
    libde265-0 \
    && rm -rf /var/lib/apt/lists/*

# Note: libheif/libde265 are required for HEIC/HEIF image support via pillow-heif

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code and Alembic migration files
COPY ./tagline_backend_app ./tagline_backend_app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "tagline_backend_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

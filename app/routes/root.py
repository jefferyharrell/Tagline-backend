"""
Root API routes for Tagline backend.
"""

from fastapi import APIRouter
import os
from ..constants import APP_NAME, API_VERSION

router = APIRouter()

APP_ENV = os.environ.get("APP_ENV", "production").lower()


@router.get("/")
def root():
    """Root endpoint: friendly in development, generic in production."""
    if APP_ENV == "development":
        return {
            "message": f"\U0001F44B Welcome to the {APP_NAME} API (development mode)!",
            "app": APP_NAME,
            "version": API_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        }
    else:
        return {"status": "ok"}

"""
Root API routes for Tagline backend.
"""

import os

from fastapi import APIRouter

from ..constants import API_VERSION, APP_NAME
from .auth import router as auth_router

router = APIRouter()

router.include_router(auth_router)

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

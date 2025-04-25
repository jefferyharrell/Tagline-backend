"""
Root API routes for Tagline backend.
"""

import os

from fastapi import APIRouter, Request

from ..constants import API_VERSION, APP_NAME
from .auth import router as auth_router
from .health import router as health_router
from .photos import router as photos_router
from .rescan import router as rescan_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(photos_router)
router.include_router(health_router)
router.include_router(rescan_router)

APP_ENV = os.environ.get("APP_ENV", "production").lower()


@router.get("/")
def root(request: Request):
    """Root endpoint: friendly in development, generic in production.
    Triggers storage provider instantiation to ensure config errors are surfaced as 503.
    """
    # Try to instantiate the provider to trigger config errors
    request.app.state.get_photo_storage_provider(request.app)
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

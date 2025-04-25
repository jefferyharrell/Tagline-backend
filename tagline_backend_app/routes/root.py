"""
Root API routes for Tagline backend.
"""

import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.deps import get_current_user
from tagline_backend_app.schemas import (
    Photo,
    PhotoMetadataFields,
    UpdateMetadataRequest,
)

from ..constants import API_VERSION, APP_NAME
from ..db import get_db
from .auth import router as auth_router
from .photos import router as photos_router
from .rescan import router as rescan_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(rescan_router)
router.include_router(photos_router)

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


@router.get("/smoke-test")
def smoke_test(request: Request):
    """Health check: verifies storage provider config. Returns 200 if OK, 503 if misconfigured."""
    provider = request.app.state.get_photo_storage_provider(request.app)
    return {"status": "ok", "provider": type(provider).__name__}


@router.patch(
    "/photos/{id}/metadata",
    response_model=Photo,
    responses={
        404: {
            "description": "Photo not found",
            "content": {"application/json": {"example": {"detail": "Photo not found"}}},
        },
        422: {
            "description": "Invalid payload or UUID supplied",
            "content": {
                "application/json": {
                    "examples": {
                        "missing": {
                            "summary": "Missing description",
                            "value": {
                                "detail": "description is required and must be a string"
                            },
                        },
                        "wrong_type": {
                            "summary": "Non-string description",
                            "value": {
                                "detail": "description is required and must be a string"
                            },
                        },
                        "bad_last_modified": {
                            "summary": "Invalid last_modified",
                            "value": {
                                "detail": "last_modified must be RFC3339/ISO8601 string"
                            },
                        },
                    }
                }
            },
        },
    },
)
def update_photo_metadata(
    id: UUID,
    payload: UpdateMetadataRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a photo's metadata (description, optionally last_modified).

    - **id**: UUID of the photo to update.
    - **payload**: UpdateMetadataRequest with metadata dict (must include `description` as a string; empty string is allowed; may include `last_modified`).
    - **Returns**: Updated Photo object.
    - **404**: Returned if photo not found.
    - **422**: Returned if validation fails (e.g., missing or non-string description, invalid last_modified).
    """
    repo = PhotoRepository(db)
    photo = repo.get(id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    metadata = payload.metadata
    description = metadata.get("description")
    if not isinstance(description, str):
        raise HTTPException(
            status_code=422, detail="description is required and must be a string"
        )

    # Optionally update last_modified if provided (must be RFC3339/ISO8601 string)
    last_modified = metadata.get("last_modified")
    if last_modified is not None:
        try:
            # This will raise if not valid ISO8601
            datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(
                status_code=422, detail="last_modified must be RFC3339/ISO8601 string"
            )

    # Update photo in DB (assume repo has update method; otherwise, simulate)
    photo.description = description.strip()
    if last_modified is not None:
        photo.updated_at = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
    db.commit()
    db.refresh(photo)
    return Photo(
        id=str(photo.id),
        object_key=photo.filename,
        metadata=PhotoMetadataFields(description=photo.description),
        last_modified=photo.updated_at.isoformat(),
    )

"""
Root API routes for Tagline backend.
"""

import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.crud.photo import PhotoRepository
from app.schemas import Photo, PhotoListResponse, PhotoMetadataFields

from ..constants import API_VERSION, APP_NAME
from ..db import get_db
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)

APP_ENV = os.environ.get("APP_ENV", "production").lower()


@router.post("/rescan", status_code=200)
def rescan_photos(request: Request, db: Session = Depends(get_db)):
    """
    Scan storage for new photos and import them into the database.
    Returns a summary of new photos imported.
    """
    # DEBUG PRINTS
    print(
        f"[DEBUG RESCAN] app.state.photo_storage_provider_kind = {request.app.state.photo_storage_provider_kind}"
    )
    print(
        f"[DEBUG RESCAN] app.state.filesystem_storage_path = {getattr(request.app.state, 'filesystem_storage_path', 'NOT SET')}"
    )

    provider = request.app.state.get_photo_storage_provider(request.app)
    print(f"[DEBUG RESCAN] provider.__class__.__name__ = {provider.__class__.__name__}")

    repo = PhotoRepository(db)
    try:
        # Only import string filenames; skip anything else (robustness for weird providers)
        storage_files = set(f for f in provider.list() if isinstance(f, str))
        db_photos = repo.list()
        db_filenames = set(photo.filename for photo in db_photos)
        new_files = storage_files - db_filenames
        imported = []
        for fname in new_files:
            photo = repo.create(filename=fname)
            imported.append(photo.filename)
        return {"imported": imported, "imported_count": len(imported)}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


@router.get(
    "/photos",
    response_model=PhotoListResponse,
    responses={
        422: {
            "description": "Invalid query parameter(s)",
            "content": {
                "application/json": {
                    "example": {"detail": "limit must be between 1 and 100"}
                }
            },
        },
    },
)
def list_photos(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """
    List photo metadata (paginated).

    - **limit**: Maximum number of photos to return (1-100, default 50)
    - **offset**: Number of photos to skip (default 0)
    - **Returns**: Paginated list of Photo objects
    - **422**: Returned if limit or offset is out of bounds
    """
    # Validate limit and offset
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=422, detail="offset must be >= 0")

    repo = PhotoRepository(db)
    photos = repo.list()
    total = len(photos)
    items = [
        Photo(
            id=str(photo.id),
            object_key=photo.filename,
            metadata=PhotoMetadataFields(description=photo.description),
            last_modified=photo.updated_at.isoformat(),
        )
        for photo in photos[offset : offset + limit]
    ]
    return PhotoListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get(
    "/photos/{id}",
    response_model=Photo,
    responses={
        404: {
            "description": "Photo not found",
            "content": {"application/json": {"example": {"detail": "Photo not found"}}},
        },
        422: {
            "description": "Invalid UUID supplied",
            "content": {
                "application/json": {"example": {"detail": "value is not a valid uuid"}}
            },
        },
    },
)
def get_photo_by_id(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single photo and its metadata by unique ID.

    - **id**: UUID of the photo to retrieve.
    - **Returns**: Photo object matching the spec.
    - **404**: Returned if no photo with the given ID exists.
    - **422**: Returned if the ID is not a valid UUID.
    """
    repo = PhotoRepository(db)
    photo = repo.get(id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return Photo(
        id=str(photo.id),
        object_key=photo.filename,
        metadata=PhotoMetadataFields(description=photo.description),
        last_modified=photo.updated_at.isoformat(),
    )


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

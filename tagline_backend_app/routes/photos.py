"""
Photos API routes for Tagline backend.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import get_current_user
from tagline_backend_app.schemas import Photo, PhotoListResponse, PhotoMetadataFields

router = APIRouter()


@router.get(
    "/photos/{id}/image",
    responses={
        200: {
            "content": {"image/jpeg": {}, "image/png": {}, "image/heic": {}},
            "description": "The image file for the photo.",
        },
        404: {
            "description": "Photo or image file not found",
            "content": {"application/json": {"example": {"detail": "Photo not found"}}},
        },
        422: {
            "description": "Invalid UUID supplied",
            "content": {
                "application/json": {"example": {"detail": "value is not a valid uuid"}}
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
def get_photo_image(
    id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieve the binary image file for a photo by unique ID.

    - **id**: UUID of the photo to retrieve.
    - **Returns**: The raw image file (not JSON).
    - **404**: Returned if no photo or file with the given ID exists.
    - **422**: Returned if the ID is not a valid UUID.
    - **500**: Returned if storage provider fails.
    """
    import mimetypes

    from fastapi.responses import StreamingResponse

    repo = PhotoRepository(db)
    photo = repo.get(id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    provider = request.app.state.get_photo_storage_provider(request.app)
    filename = photo.filename
    # Guess MIME type from filename
    media_type, _ = mimetypes.guess_type(filename)
    if not media_type:
        # Default to application/octet-stream if unknown
        media_type = "application/octet-stream"
    try:
        fileobj = provider.retrieve(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Photo file not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    return StreamingResponse(fileobj, media_type=media_type)


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
def get_photo_by_id(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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
    current_user=Depends(get_current_user),
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

"""
Photos API routes for Tagline backend.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import get_current_user
from tagline_backend_app.schemas import Photo, PhotoListResponse, PhotoMetadataFields

router = APIRouter()


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

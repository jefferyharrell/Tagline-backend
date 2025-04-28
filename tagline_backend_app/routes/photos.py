"""
Photos API routes for Tagline backend.
"""

# Imports for thumbnail generation
import io
import logging
from datetime import datetime
from uuid import UUID

import pillow_heif  # Ensure it's imported, though registration happens in main
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from PIL import Image
from sqlalchemy.orm import Session

from tagline_backend_app.caching import get_image_cache, get_thumbnail_cache
from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import get_current_user
from tagline_backend_app.schemas import (
    Photo,
    PhotoListResponse,
    PhotoMetadataFields,
    UpdateMetadataRequest,
)

router = APIRouter()

logger = logging.getLogger(__name__)


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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns a 1024x1024 padded JPEG of the photo (not the original), with in-memory LRU caching.

    - **id**: UUID of the photo to retrieve.
    - **Returns**: 1024x1024 JPEG image (padded as needed).
    - **404**: If photo or file not found.
    - **422**: If ID is not a valid UUID.
    - **500**: If storage or processing fails.
    """
    import io
    import logging
    import traceback

    import pillow_heif
    from PIL import Image

    # 1. Validate UUID
    if not isinstance(id, UUID):
        logging.error(f"Invalid UUID in get_photo_image: {id}")
        raise HTTPException(status_code=422, detail="Invalid UUID format")

    # 2. Get photo metadata
    repo = PhotoRepository(db)
    try:
        photo = repo.get(id)
        if photo is None:
            raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as exc:
        logging.error(
            f"DB error getting photo {id} for image: {exc}\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=500, detail="Database error")

    # 3. Check image cache
    cache = get_image_cache()
    cache_key = str(id)
    if cache is not None and cache_key in cache:
        logging.debug(f"Image cache hit for {id}")
        return Response(content=cache[cache_key], media_type="image/jpeg")

    # 4. Get original image from storage
    provider = request.app.state.get_photo_storage_provider(request.app)
    filename = photo.filename
    try:
        image_bytes_io = provider.retrieve(filename)
        if not image_bytes_io:
            raise FileNotFoundError
        image_data = image_bytes_io.read()
        if not image_data:
            raise ValueError("Image file is empty")
    except FileNotFoundError:
        logging.warning(f"Original image file not found for photo {id}: {filename}")
        raise HTTPException(status_code=404, detail="Original image file not found")
    except Exception as exc:
        logging.error(f"Storage error retrieving {filename} for image: {exc}")
        raise HTTPException(status_code=500, detail="Storage provider error")

    # 5. Generate 1024x1024 padded JPEG
    try:
        # Ensure pillow_heif is registered (should be via main.py lifespan)
        if (
            not pillow_heif.is_supported(io.BytesIO(image_data))
            and not Image.open(io.BytesIO(image_data)).format
        ):
            pillow_heif.register_heif_opener()
        img = Image.open(io.BytesIO(image_data))
        # Convert to RGB for JPEG
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Resize so the longest edge is 1024px, preserving aspect ratio
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        # Save the resized image to JPEG in memory (no padding)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()
    except Exception:
        logging.exception(f"Error generating fullsize image for photo {id}")
        raise HTTPException(status_code=500, detail="Image processing failed")

    # 6. Cache the result
    if cache is not None:
        try:
            cache[cache_key] = image_bytes
            logging.debug(
                f"Cached 1024x1024 image for photo {id} ({len(image_bytes)/1024:.1f} KB)"
            )
        except Exception as exc:
            logging.error(f"Failed to cache image for photo {id}: {exc}")

    # 7. Return the image
    return Response(content=image_bytes, media_type="image/jpeg")


@router.get(
    "/photos/{id}/thumbnail",
    responses={
        200: {
            "content": {"image/webp": {}},
            "description": "A 512x512 WebP thumbnail for the photo.",
        },
        404: {
            "description": "Photo, image file, or thumbnail not found/creatable",
            "content": {"application/json": {"example": {"detail": "Not Found"}}},
        },
        422: {
            "description": "Invalid UUID supplied",
            "content": {
                "application/json": {"example": {"detail": "value is not a valid uuid"}}
            },
        },
        500: {
            "description": "Internal server error during thumbnail generation",
            "content": {
                "application/json": {
                    "example": {"detail": "Thumbnail generation failed"}
                }
            },
        },
    },
    # Tell FastAPI this route returns a Response directly, not JSON
    response_class=Response,
)
def get_photo_thumbnail(
    id: UUID,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a 512x512 lossy WebP thumbnail for a photo by unique ID.

    - **id**: UUID of the photo to retrieve the thumbnail for.
    - **Returns**: Raw WebP image bytes.
    - **404**: Returned if photo or original image not found, or if image format is unsupported/corrupt.
    - **422**: Returned if the ID is not a valid UUID.
    - **500**: Returned if thumbnail generation fails unexpectedly.
    """
    cache = get_thumbnail_cache()
    cache_key = f"thumbnail:{id}"

    # 1. Check cache
    if cache is not None:
        cached_thumbnail = cache.get(cache_key)
        if cached_thumbnail:
            logger.debug(f"Thumbnail cache HIT for photo_id: {id}")
            return Response(content=cached_thumbnail, media_type="image/webp")
        else:
            logger.debug(f"Thumbnail cache MISS for photo_id: {id}")

    # 2. Get photo metadata from DB
    repo = PhotoRepository(db)
    try:
        photo = repo.get(id)
        if photo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Photo metadata not found"
            )
    except Exception as e:
        logger.error(f"DB error getting photo {id} for thumbnail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )

    # 3. Get original image from storage
    provider = request.app.state.get_photo_storage_provider(request.app)
    filename = photo.filename
    try:
        image_bytes_io = provider.retrieve(filename)
        if not image_bytes_io:
            raise FileNotFoundError  # Should be caught below
        # Read all bytes into memory for Pillow
        image_data = image_bytes_io.read()
        if not image_data:
            raise ValueError("Image file is empty")

    except FileNotFoundError:
        logger.warning(
            f"Original image file not found in storage for photo {id}: {filename}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original image file not found",
        )
    except Exception as e:
        logger.error(f"Storage error retrieving {filename} for thumbnail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Storage provider error",
        )

    # 4. Generate thumbnail
    try:
        # Ensure pillow_heif is registered (should be via main.py lifespan)
        if (
            not pillow_heif.is_supported(io.BytesIO(image_data))
            and not Image.open(io.BytesIO(image_data)).format
        ):
            pillow_heif.register_heif_opener()  # Attempt registration again just in case?

        img = Image.open(io.BytesIO(image_data))

        # Ensure image is in RGB or RGBA mode for WebP saving
        if img.mode not in ["RGB", "RGBA"]:
            logger.debug(
                f"Converting image {id} from mode {img.mode} to RGBA for thumbnail."
            )
            img = img.convert("RGBA")

        # Create the thumbnail, maintaining aspect ratio, fitting within 512x512
        img.thumbnail((512, 512), Image.Resampling.LANCZOS)

        # Create a new 512x512 blank RGBA image (transparent background)
        thumbnail_bg = Image.new("RGBA", (512, 512), (255, 255, 255, 0))

        # Calculate position to paste the thumbnail in the center
        paste_x = (512 - img.width) // 2
        paste_y = (512 - img.height) // 2

        # Paste the thumbnail onto the background
        thumbnail_bg.paste(
            img, (paste_x, paste_y), img if img.mode == "RGBA" else None
        )  # Use mask if RGBA

        # Save to a bytes buffer as lossy WebP
        buffer = io.BytesIO()
        # Use RGBA to preserve potential transparency from PNGs/HEICs
        thumbnail_bg.save(
            buffer, format="WEBP", quality=80, method=4
        )  # method=4 is a good balance
        thumbnail_bytes = buffer.getvalue()

    except Exception:
        logger.exception(
            f"Unexpected error generating thumbnail for photo {id}"
        )  # Use logger.exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Thumbnail generation failed",
        )

    # 5. Cache the result
    if cache is not None:
        try:
            # Estimate size for logging, not for cachetools itself
            size_kb = len(thumbnail_bytes) / 1024
            cache[cache_key] = thumbnail_bytes
            logger.debug(f"Cached thumbnail for photo {id} ({size_kb:.1f} KB)")
        except Exception as e:
            # Log caching errors but don't fail the request
            logger.error(f"Failed to cache thumbnail for photo {id}: {e}")

    # 6. Return thumbnail
    return Response(content=thumbnail_bytes, media_type="image/webp")


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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
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
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
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
    current_user=Depends(get_current_user),
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

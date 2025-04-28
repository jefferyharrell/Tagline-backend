"""
Rescan API route for Tagline backend.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import verify_api_key

router = APIRouter()


@router.post("/rescan", status_code=200)
def rescan_photos(
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(verify_api_key),
):
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
    repo = PhotoRepository(db)

    try:
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

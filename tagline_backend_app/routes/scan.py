"""
Rescan API route for Tagline backend.
"""

import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from tagline_backend_app.crud.photo import PhotoRepository
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import verify_api_key

router = APIRouter()


# In-memory lock for scan idempotency (attach to app.state on startup)
def get_scan_lock(app):
    if not hasattr(app.state, "scan_lock"):
        app.state.scan_lock = asyncio.Lock()
    return app.state.scan_lock


@router.post("/scan", status_code=200)
def scan_photos(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(verify_api_key),
):
    """
    Async/idempotent scan endpoint. Starts a scan if not already running.
    Returns status: "started" or "already_running".
    """
    app = request.app
    scan_lock = get_scan_lock(app)
    if scan_lock.locked():
        return {"status": "already_running"}

    def scan_logic():
        # Real scan logic: import new photos with metadata
        import logging

        from PIL import Image, UnidentifiedImageError

        provider = app.state.get_photo_storage_provider(app)
        repo = PhotoRepository(db)
        try:
            storage_files = set(f for f in provider.list() if isinstance(f, str))
            db_photos = repo.list()
            db_filenames = set(photo.filename for photo in db_photos)
            new_files = storage_files - db_filenames
            imported = []
            for fname in new_files:
                logging.debug(f"[scan] Processing file: {fname}")
                width = height = None
                try:
                    with provider.retrieve(fname) as f:
                        with Image.open(f) as img:
                            width, height = img.width, img.height
                    logging.debug(
                        f"[scan] Extracted: {fname} width={width} height={height}"
                    )
                except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
                    logging.warning(
                        f"[scan] Skipping unreadable/corrupt image '{fname}': {e}"
                    )
                    continue
                # Add more metadata extraction here as needed
                photo = repo.create(
                    filename=fname, metadata={"width": width, "height": height}
                )
                imported.append(photo.filename)
                logging.info(
                    f"[scan] Imported: {fname} (width={width}, height={height})"
                )
            # Optionally: store results in app.state for /health, etc.
        except Exception as e:
            logging.error(f"Scan failed: {e}")
            # Optionally: store error in app.state
        finally:
            # Release lock if needed (asyncio.Lock auto-releases with context mgr)
            pass

    async def scan_wrapper():
        async with scan_lock:
            scan_logic()

    background_tasks.add_task(scan_wrapper)
    return {"status": "started"}

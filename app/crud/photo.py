"""
CRUD repository for Photo model.
"""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Photo


class PhotoRepository:
    """Repository for Photo CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        filename: str,
        metadata: Optional[dict[str, object]] = None,
    ) -> Photo:
        """
        Create and persist a new Photo.
        Args:
            filename: The name of the photo file.
            metadata: Dict of supported metadata fields. Currently supports 'description'.
        Returns:
            The created Photo instance.
        """
        meta = metadata or {}
        desc = meta.get("description")
        photo = Photo(filename=filename, description=desc)
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def get(self, photo_id: uuid.UUID) -> Optional[Photo]:
        """Get a Photo by its ID."""
        return self.db.get(Photo, photo_id)

    def list(self) -> List[Photo]:
        """List all Photos."""
        return self.db.query(Photo).all()

    def update(
        self,
        photo_id: uuid.UUID,
        filename: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Photo]:
        """Update a Photo's filename and/or description."""
        photo = self.get(photo_id)
        if not photo:
            return None
        if filename is not None:
            photo.filename = filename
        if description is not None:
            photo.description = description
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def delete(self, photo_id: uuid.UUID) -> None:
        """Delete a Photo by its ID."""
        photo = self.get(photo_id)
        if photo:
            self.db.delete(photo)
            self.db.commit()

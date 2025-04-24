"""
NullPhotoStorageProvider: a /dev/null implementation for Tagline.
Accepts all operations, stores nothing, returns nothing, never raises config errors.
Useful for CI, demo, or when no real storage is needed.
"""

from typing import BinaryIO, Iterable, Optional

from .provider import PhotoStorageProvider


class NullPhotoStorageProvider(PhotoStorageProvider):
    """
    /dev/null provider: accepts all, returns nothing.
    - list: always empty
    - retrieve: always raises FileNotFoundError
    - upload/delete: no-op
    - get_url: always None
    """

    def list(self, prefix: Optional[str] = None) -> Iterable[str]:
        return []

    def retrieve(self, key: str) -> BinaryIO:
        raise FileNotFoundError(f"Null provider: '{key}' does not exist (nothing does)")

    def upload(self, key: str, data: BinaryIO) -> None:
        pass  # No-op

    def delete(self, key: str) -> None:
        pass  # No-op

    def get_url(self, key: str) -> Optional[str]:
        return None

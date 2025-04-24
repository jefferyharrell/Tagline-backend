"""
InMemoryPhotoStorageProvider: ephemeral, in-memory storage for Tagline.
Stores files in a process-local dict; wiped on restart. Great for tests and CI!
"""

from io import BytesIO
from typing import BinaryIO, Dict, Iterable, Optional

from .provider import PhotoStorageProvider


class InMemoryPhotoStorageProvider(PhotoStorageProvider):
    """
    In-memory provider: stores files in a dict, lost on process exit.
    - list: returns all stored keys
    - retrieve: returns BytesIO for stored key, raises FileNotFoundError if missing
    - upload: stores bytes under key
    - delete: removes key if present
    - get_url: always None
    """

    def __init__(self):
        self._store: Dict[str, bytes] = {}

    def list(self, prefix: Optional[str] = None) -> Iterable[str]:
        if prefix is None:
            return list(self._store.keys())
        return [k for k in self._store if k.startswith(prefix)]

    def retrieve(self, key: str) -> BinaryIO:
        if key not in self._store:
            raise FileNotFoundError(f"In-memory provider: '{key}' not found")
        return BytesIO(self._store[key])

    def upload(self, key: str, data: BinaryIO) -> None:
        self._store[key] = data.read()

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def get_url(self, key: str) -> Optional[str]:
        return None

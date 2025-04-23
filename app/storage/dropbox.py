"""
Dropbox implementation of PhotoStorageProvider (stub).
All methods raise NotImplementedError. This is a placeholder for future Dropbox integration.
"""

from typing import BinaryIO, Iterable, Optional

from app.storage.provider import PhotoStorageProvider


class DropboxPhotoStorageProvider(PhotoStorageProvider):
    """
    Photo storage provider using Dropbox (NOT IMPLEMENTED).
    All methods raise NotImplementedError.
    """

    def __init__(self, access_token: str, root_path: Optional[str] = None):
        self.access_token = access_token
        self.root_path = root_path or "/"
        raise NotImplementedError("DropboxPhotoStorageProvider is not implemented yet.")

    def list(self, prefix: Optional[str] = None) -> Iterable[str]:
        raise NotImplementedError("Dropbox provider is not implemented yet.")

    def retrieve(self, key: str) -> BinaryIO:
        raise NotImplementedError("Dropbox provider is not implemented yet.")

    # upload and delete would go here, also raising NotImplementedError

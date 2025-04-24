"""
Local filesystem implementation of PhotoStorageProvider.
All file operations are sandboxed to a configured root directory.
This provider is read-only: upload and delete are not supported.
"""

from pathlib import Path
from typing import BinaryIO, Iterable, Optional

from app.storage.provider import PhotoStorageProvider


class StorageProviderMisconfigured(Exception):
    """
    Raised when a storage provider is misconfigured (e.g., missing required env vars).
    """

    pass


class FilesystemPhotoStorageProvider(PhotoStorageProvider):
    """
    Photo storage provider using the local filesystem (read-only).
    All keys are paths relative to the configured root directory.
    Prevents path traversal and access outside the root.
    """

    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize the provider with a root directory.
        Args:
            root_path: pathlib.Path to the photo storage root directory, or None.
        Raises:
            StorageProviderMisconfigured: If root_path is None or invalid.
        """
        if root_path is None:
            raise StorageProviderMisconfigured(
                "FILESYSTEM_STORAGE_PATH is not set. The filesystem provider cannot operate without a root directory."
            )
        root = root_path.resolve()
        if not root.is_dir():
            raise StorageProviderMisconfigured(
                f"Photo storage root does not exist or is not a directory: {root_path}"
            )
        self._root = root

    def list(self, prefix: Optional[str] = None) -> Iterable[str]:
        """
        List all photo keys (relative paths) in the root directory, optionally filtered by prefix.
        Args:
            prefix: Optional string to filter returned keys.
        Returns:
            Iterable of keys (relative paths from root).
        """
        for file in self._root.rglob("*"):
            if file.is_file():
                rel_path = str(file.relative_to(self._root))
                if prefix is None or rel_path.startswith(prefix):
                    yield rel_path

    def retrieve(self, key: str) -> BinaryIO:
        """
        Retrieve a photo by key (relative path from root).
        Args:
            key: Relative path to the file under root.
        Returns:
            BinaryIO file-like object opened in 'rb' mode.
        Raises:
            FileNotFoundError: If the file does not exist or is outside the root.
        """
        # Compose the path and resolve it
        file_path = (self._root / key).resolve()
        try:
            file_path.relative_to(self._root)
        except ValueError:
            raise FileNotFoundError(f"Access denied: {key}")
        if not file_path.is_file():
            raise FileNotFoundError(f"Photo not found: {key}")
        return file_path.open("rb")

    # upload and delete are inherited (NotImplementedError)

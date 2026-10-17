"""C8 · One storage interface, two implementations. Functions marked TODO(you) are yours."""
from __future__ import annotations

from pathlib import Path


class LocalStorage:
    """Keys are relative paths under root. Used for local runs and tests."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def put(self, key: str, data: bytes) -> None:
        """TODO(you): write bytes, creating parent folders."""
        raise NotImplementedError

    def get(self, key: str) -> bytes:
        """TODO(you): read bytes. KeyError if missing."""
        raise NotImplementedError

    def list(self, prefix: str = "") -> list[str]:
        """TODO(you): sorted keys starting with prefix."""
        raise NotImplementedError


class S3Storage:
    """Same interface over boto3. `client` is injectable so tests never touch AWS."""

    def __init__(self, bucket: str, client=None):
        self.bucket = bucket
        self._client = client

    @property
    def client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("s3")
        return self._client

    def put(self, key: str, data: bytes) -> None:
        """TODO(you): put_object."""
        raise NotImplementedError

    def get(self, key: str) -> bytes:
        """TODO(you): get_object, read the Body."""
        raise NotImplementedError

    def list(self, prefix: str = "") -> list[str]:
        """TODO(you): list_objects_v2; Contents may be absent."""
        raise NotImplementedError

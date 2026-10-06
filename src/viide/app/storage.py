from datetime import timedelta
from typing import BinaryIO, Protocol

from pydantic import HttpUrl


class Storage(Protocol):
    def put(self, key: str, stream: BinaryIO, content_type: str) -> None: ...

    def get(self, key: str, expires_in: timedelta) -> HttpUrl: ...

    def delete(self, key: str) -> None: ...

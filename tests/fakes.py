from datetime import UTC, datetime, timedelta
from typing import BinaryIO

from pydantic import HttpUrl

from viide.app.aka.errors import ShortCodeTaken
from viide.app.aka.links import Link, LinkRepository, NewLink
from viide.app.aka.qr import NewQrCode, QrCode, QrRepository
from viide.app.auth.client import Client
from viide.app.auth.user import Credentials
from viide.app.storage import Storage, StorageUnavailable


class FakeLinkRepository(LinkRepository):
    def __init__(self) -> None:
        self.rows: dict[str, Link] = {}
        self.refuse_connect = False
        self.fail_connect = False

    def seed(self, dst: str, created_by: str = "alice", expires_at: datetime | None = None) -> Link:
        src = HttpUrl("https://example.com")
        return self.add(NewLink(src=src, dst=dst, created_by=created_by, expires_at=expires_at))

    def add(self, link: NewLink) -> Link:
        if link.dst in self.rows:
            raise ShortCodeTaken
        row = Link(**link.model_dump(), created_at=datetime.now(UTC), connected_to=None)
        self.rows[row.dst] = row
        return row

    def get(self, dst: str) -> Link | None:
        return self.rows.get(dst)

    def owned_by(self, created_by: str) -> list[Link]:
        return [row for row in self.rows.values() if row.created_by == created_by]

    def connect(self, dst: str, qr_id: int) -> bool:
        if self.fail_connect:
            raise RuntimeError("database down")
        if self.refuse_connect:
            return False
        self.rows[dst] = self.rows[dst].model_copy(update={"connected_to": qr_id})
        return True

    def delete(self, dst: str) -> None:
        self.rows.pop(dst, None)


class FakeQrRepository(QrRepository):
    def __init__(self) -> None:
        self.rows: dict[int, QrCode] = {}
        self.fail_add = False

    def add(self, qr: NewQrCode) -> QrCode:
        if self.fail_add:
            raise RuntimeError("database down")
        row = QrCode(**qr.model_dump(), id=len(self.rows) + 1, created_at=datetime.now(UTC))
        self.rows[row.id] = row
        return row

    def get(self, qr_id: int) -> QrCode | None:
        return self.rows.get(qr_id)

    def delete(self, qr_id: int) -> None:
        self.rows.pop(qr_id, None)


class FakeStorage(Storage):
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.fail_put = False
        self.fail_get = False
        self.fail_delete = False

    def put(self, key: str, stream: BinaryIO, content_type: str) -> None:
        if self.fail_put:
            raise StorageUnavailable
        self.objects[key] = stream.read()

    def get(self, key: str, expires_in: timedelta) -> HttpUrl:
        if self.fail_get:
            raise StorageUnavailable
        return HttpUrl(f"https://storage.test/{key}")

    def delete(self, key: str) -> None:
        if self.fail_delete:
            raise StorageUnavailable
        self.objects.pop(key, None)


class FakeAuthClient(Client):
    def __init__(self) -> None:
        self.accepts = True
        self.error: Exception | None = None
        self.calls = 0

    def verify_credentials(self, creds: Credentials) -> bool:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.accepts

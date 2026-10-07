import io

import pytest
import zxingcpp
from PIL import Image

from viide.app.aka.errors import LinkNotFound, QrUnavailable
from viide.app.aka.manager import LinkManager

from .fakes import FakeLinkRepository, FakeQrRepository, FakeStorage


def test_stores_qr_as_png(manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage):
    links.seed("code")

    manager.create_qr("code", created_by="alice")

    (image,) = storage.objects.values()
    assert image.startswith(b"\x89PNG")


def decode_qr(image: bytes) -> str:
    (result,) = zxingcpp.read_barcodes(Image.open(io.BytesIO(image)))
    return result.text


def test_dynamic_qr_encodes_short_url(manager: LinkManager, storage: FakeStorage):
    manager.shorten("https://example.com/page", created_by="alice", dst="code")

    manager.create_qr("code", created_by="alice")

    (image,) = storage.objects.values()
    assert decode_qr(image) == "https://viide.test/code"


def test_static_qr_encodes_original_url(manager: LinkManager, storage: FakeStorage):
    link = manager.shorten("https://example.com/page", created_by="alice", static=True)

    manager.create_qr(link.dst, created_by="alice")

    (image,) = storage.objects.values()
    assert decode_qr(image) == "https://example.com/page"


def test_connects_qr_to_link(
    manager: LinkManager, links: FakeLinkRepository, qr_codes: FakeQrRepository
):
    links.seed("code")

    manager.create_qr("code", created_by="alice")

    (qr,) = qr_codes.rows.values()
    assert links.rows["code"].connected_to == qr.id


def test_listed_link_shows_qr(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code")
    manager.create_qr("code", created_by="alice")

    (item,) = manager.owned_by("alice")

    assert item.qr_url is not None


def test_second_request_creates_nothing(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")

    manager.create_qr("code", created_by="alice")
    manager.create_qr("code", created_by="alice")

    assert len(storage.objects) == 1


def test_cannot_create_qr_for_other_users_link(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", created_by="bob")

    with pytest.raises(LinkNotFound):
        manager.create_qr("code", created_by="alice")


def test_storage_failure_makes_qr_unavailable(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")
    storage.fail_put = True

    with pytest.raises(QrUnavailable):
        manager.create_qr("code", created_by="alice")


def test_database_failure_removes_stored_image(
    manager: LinkManager,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
):
    links.seed("code")
    qr_codes.fail_add = True

    with pytest.raises(RuntimeError):
        manager.create_qr("code", created_by="alice")
    assert storage.objects == {}


def test_failed_cleanup_is_logged(
    manager: LinkManager,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
    caplog: pytest.LogCaptureFixture,
):
    links.seed("code")
    qr_codes.fail_add = True
    storage.fail_delete = True

    with pytest.raises(RuntimeError):
        manager.create_qr("code", created_by="alice")
    assert "Could not delete stored object" in caplog.text


def test_lost_race_removes_new_qr(
    manager: LinkManager,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
):
    links.seed("code")
    links.refuse_connect = True

    manager.create_qr("code", created_by="alice")

    assert qr_codes.rows == {}
    assert storage.objects == {}


def test_connect_failure_cleans_up_qr_and_image(
    manager: LinkManager,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
):
    links.seed("code")
    links.fail_connect = True

    with pytest.raises(RuntimeError):
        manager.create_qr("code", created_by="alice")
    assert qr_codes.rows == {}
    assert storage.objects == {}


def test_signing_failure_hides_qr(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")
    manager.create_qr("code", created_by="alice")
    storage.fail_get = True

    (item,) = manager.owned_by("alice")

    assert item.qr_url is None


def test_deleting_link_removes_its_qr(
    manager: LinkManager,
    links: FakeLinkRepository,
    qr_codes: FakeQrRepository,
    storage: FakeStorage,
):
    links.seed("code")
    manager.create_qr("code", created_by="alice")

    manager.delete("code", created_by="alice")

    assert qr_codes.rows == {}
    assert storage.objects == {}


def test_deleting_link_survives_storage_failure(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")
    manager.create_qr("code", created_by="alice")
    storage.fail_delete = True

    manager.delete("code", created_by="alice")

    assert "code" not in links.rows


def test_missing_qr_row_hides_qr(
    manager: LinkManager, links: FakeLinkRepository, qr_codes: FakeQrRepository
):
    links.seed("code")
    manager.create_qr("code", created_by="alice")
    qr_codes.rows.clear()

    (item,) = manager.owned_by("alice")

    assert item.qr_url is None


def test_deleting_link_survives_missing_qr_row(
    manager: LinkManager, links: FakeLinkRepository, qr_codes: FakeQrRepository
):
    links.seed("code")
    manager.create_qr("code", created_by="alice")
    qr_codes.rows.clear()

    manager.delete("code", created_by="alice")

    assert "code" not in links.rows

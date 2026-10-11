import base64
import io

import pytest
import zxingcpp
from PIL import Image

from viide.app.aka.errors import LinkNotFound
from viide.app.aka.manager import LinkManager

from .fakes import FakeLinkRepository, FakeStorage


def test_qr_returns_png_data_uri_without_storage(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")

    image = manager.create_qr("code", created_by="alice")

    assert image.startswith("data:image/png;base64,")
    payload = base64.b64decode(image.removeprefix("data:image/png;base64,"))
    assert payload.startswith(b"\x89PNG"), "the returned QR image should be a PNG"
    assert storage.objects == {}, "QR images should not be stored"


def decode_qr(image: bytes) -> str:
    (result,) = zxingcpp.read_barcodes(Image.open(io.BytesIO(image)))
    return result.text


def test_dynamic_qr_returns_short_url_image_without_storage(
    manager: LinkManager, storage: FakeStorage
):
    link = manager.shorten("https://example.com/page", created_by="alice")

    image = manager.create_qr(link.dst, created_by="alice")

    payload = base64.b64decode(image.removeprefix("data:image/png;base64,"))
    assert decode_qr(payload) == f"https://viide.test/{link.dst}"
    assert storage.objects == {}, "dynamic QR images should not be stored"


def test_static_qr_generates_from_url_without_link_or_storage(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    image = manager.create_qr("https://example.com/page", static=True)

    payload = base64.b64decode(image.removeprefix("data:image/png;base64,"))
    assert decode_qr(payload) == "https://example.com/page"
    assert links.rows == {}, "static QR generation should not create a link"
    assert storage.objects == {}, "static QR images should not be stored"


def test_repeated_qr_requests_generate_without_persistence(
    manager: LinkManager, links: FakeLinkRepository, storage: FakeStorage
):
    links.seed("code")

    first = manager.create_qr("code", created_by="alice")
    second = manager.create_qr("code", created_by="alice")

    assert first is not None and second is not None
    assert storage.objects == {}, "QR requests should not persist images"


def test_cannot_create_qr_for_other_users_link(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", created_by="bob")

    with pytest.raises(LinkNotFound):
        manager.create_qr("code", created_by="alice")

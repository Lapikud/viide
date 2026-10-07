import secrets
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import HttpUrl

from viide.app.aka.errors import (
    InvalidExpiry,
    InvalidShortCode,
    InvalidUrl,
    LinkNotFound,
    ReservedShortCode,
    ShortCodeGenerationFailed,
    ShortCodeTaken,
)
from viide.app.aka.manager import LinkManager

from .fakes import FakeLinkRepository

URL = "https://example.com"
YESTERDAY = datetime.now(UTC) - timedelta(days=1)
TOMORROW = datetime.now(UTC) + timedelta(days=1)


def generate_codes(monkeypatch: pytest.MonkeyPatch, *codes: str) -> None:
    supply = iter(codes)
    monkeypatch.setattr(secrets, "token_urlsafe", lambda _: next(supply))


@pytest.mark.parametrize("src", ["", "not a url", "example.com", "ftp://example.com"])
def test_rejects_invalid_url(manager: LinkManager, src: str):
    with pytest.raises(InvalidUrl):
        manager.shorten(src, created_by="alice")


@pytest.mark.parametrize("dst", ["has space", "bang!", "a/b", "x" * 256])
def test_rejects_invalid_short_code(manager: LinkManager, dst: str):
    with pytest.raises(InvalidShortCode):
        manager.shorten(URL, created_by="alice", dst=dst)


@pytest.mark.parametrize("days", ["0", "-1", "3651", "abc"])
def test_rejects_invalid_expiry(manager: LinkManager, days: str):
    with pytest.raises(InvalidExpiry):
        manager.shorten(URL, created_by="alice", expires_in_days=days)


def test_saves_link_with_custom_code(manager: LinkManager, links: FakeLinkRepository):
    manager.shorten(URL, created_by="alice", dst="my-code")

    assert links.rows["my-code"].created_by == "alice", "the custom link should belong to Alice"
    assert links.rows["my-code"].src == HttpUrl(URL), "the custom link should keep its target URL"


def test_link_without_expiry_never_expires(manager: LinkManager):
    link = manager.shorten(URL, created_by="alice", dst="code")

    assert link.expires_at is None, "a link without an expiry should have no deadline"


def test_expiry_is_days_from_now(manager: LinkManager):
    link = manager.shorten(URL, created_by="alice", dst="code", expires_in_days="7")

    assert link.expires_at is not None, "the link should have an expiry time"
    expected = datetime.now(UTC) + timedelta(days=7)
    assert abs(link.expires_at - expected) < timedelta(seconds=5), (
        "the expiry should be seven days from creation"
    )


def test_blank_code_and_expiry_are_ignored(manager: LinkManager, monkeypatch: pytest.MonkeyPatch):
    generate_codes(monkeypatch, "random")

    link = manager.shorten(URL, created_by="alice", dst=" ", expires_in_days="")

    assert link.dst == "random", "a blank code should trigger code generation"
    assert link.expires_at is None, "a blank expiry should leave the link without a deadline"


def test_rejects_reserved_code(manager: LinkManager):
    with pytest.raises(ReservedShortCode):
        manager.shorten(URL, created_by="alice", dst="login")


def test_rejects_taken_code(manager: LinkManager, links: FakeLinkRepository):
    links.seed("taken")

    with pytest.raises(ShortCodeTaken):
        manager.shorten(URL, created_by="bob", dst="taken")


def test_generated_code_skips_reserved(manager: LinkManager, monkeypatch: pytest.MonkeyPatch):
    generate_codes(monkeypatch, "login", "random")

    link = manager.shorten(URL, created_by="alice")

    assert link.dst == "random", "a reserved code should be skipped"


def test_generated_code_retries_when_taken(
    manager: LinkManager, links: FakeLinkRepository, monkeypatch: pytest.MonkeyPatch
):
    links.seed("taken")
    generate_codes(monkeypatch, "taken", "random")

    link = manager.shorten(URL, created_by="alice")

    assert link.dst == "random", "a collision should trigger another generated code"


def test_generated_code_can_be_retried_after_collisions(
    manager: LinkManager, links: FakeLinkRepository, monkeypatch: pytest.MonkeyPatch
):
    links.seed("taken")
    generate_codes(monkeypatch, *["taken"] * 5, "available")

    with pytest.raises(
        ShortCodeGenerationFailed,
        match="Could not generate a short code. Please try again.",
    ):
        manager.shorten(URL, created_by="alice")

    link = manager.shorten(URL, created_by="alice")

    assert link.dst == "available", "a later request should use the available code"


def test_resolves_active_link(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", expires_at=TOMORROW)

    assert manager.resolve("code").dst == "code", "an active short code should resolve"


def test_resolving_missing_link_fails(manager: LinkManager):
    with pytest.raises(LinkNotFound):
        manager.resolve("missing")


def test_resolving_expired_link_fails(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", expires_at=YESTERDAY)

    with pytest.raises(LinkNotFound):
        manager.resolve("code")


def test_lists_only_own_links(manager: LinkManager, links: FakeLinkRepository):
    links.seed("mine")
    links.seed("theirs", created_by="bob")

    owned = manager.owned_by("alice")

    assert [item.link.dst for item in owned] == ["mine"], (
        "the owner should see only their own links"
    )


def test_listed_link_has_short_url(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code")

    (item,) = manager.owned_by("alice")

    assert str(item.short_url) == "https://viide.test/code", (
        "the listing should show the public short URL"
    )


def test_static_link_has_no_short_url(manager: LinkManager):
    manager.shorten(URL, created_by="alice", static=True)

    (item,) = manager.owned_by("alice")

    assert item.short_url is None, "a static link should not have a short URL"


def test_listed_link_shows_expired(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", expires_at=YESTERDAY)

    (item,) = manager.owned_by("alice")

    assert item.expired, "the listing should mark an expired link"


def test_user_can_delete_own_link(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code")

    manager.delete("code", created_by="alice")

    assert "code" not in links.rows, "the owner should be able to delete the link"


def test_user_cannot_delete_other_users_link(manager: LinkManager, links: FakeLinkRepository):
    links.seed("code", created_by="bob")

    with pytest.raises(LinkNotFound):
        manager.delete("code", created_by="alice")
    assert "code" in links.rows, "another user should not delete the link"

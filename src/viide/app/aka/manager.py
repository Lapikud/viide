"""Short link and QR code manager."""

import io
import logging
import secrets
from datetime import UTC, datetime, timedelta

import qrcode
from pydantic import HttpUrl, ValidationError

from viide.app.storage import Storage, StorageUnavailable

from .errors import (
    InvalidExpiry,
    InvalidLink,
    InvalidShortCode,
    InvalidUrl,
    LinkError,
    LinkNotFound,
    QrUnavailable,
    ReservedShortCode,
    ShortCodeTaken,
)
from .links import Link, LinkDetails, LinkRepository, NewLink, ShortenRequest
from .qr import NewQrCode, QrRepository

logger = logging.getLogger(__name__)

ATTEMPTS = 5
QR_URL_LIFETIME = timedelta(hours=1)
FIELD_ERRORS: dict[str, type[LinkError]] = {
    "src": InvalidUrl,
    "dst": InvalidShortCode,
    "expires_in_days": InvalidExpiry,
}


class LinkManager:
    """Manage links, ownership, expiry, and QR images."""

    def __init__(
        self,
        links: LinkRepository,
        qr_codes: QrRepository,
        storage: Storage,
        public_url: HttpUrl,
        reserved: frozenset[str],
    ) -> None:
        """Set up link, QR code, and storage services."""
        self.links = links
        self.qr_codes = qr_codes
        self.storage = storage
        self.public_url = str(public_url).rstrip("/")
        self.reserved = reserved

    def shorten(
        self,
        src: str,
        created_by: str,
        dst: str | None = None,
        expires_in_days: str | int | None = None,
    ) -> Link:
        """Validate and create a link with a custom or generated short code."""
        request = self.__validate(src, dst, expires_in_days)
        expires_at = (
            datetime.now(UTC) + timedelta(days=request.expires_in_days)
            if request.expires_in_days
            else None
        )

        if request.dst:
            if request.dst in self.reserved:
                raise ReservedShortCode
            return self.links.add(
                NewLink(
                    src=request.src, dst=request.dst, created_by=created_by, expires_at=expires_at
                )
            )

        for _ in range(ATTEMPTS):
            code = secrets.token_urlsafe(5)
            if code in self.reserved:
                continue
            try:
                return self.links.add(
                    NewLink(src=request.src, dst=code, created_by=created_by, expires_at=expires_at)
                )
            except ShortCodeTaken:
                continue
        raise ShortCodeTaken

    def resolve(self, dst: str) -> Link:
        """Find an active link or raise LinkNotFound."""
        link = self.links.get(dst)
        if link is None or self.__is_expired(link):
            raise LinkNotFound
        return link

    def owned_by(self, created_by: str) -> list[LinkDetails]:
        """List the user's links with URLs and expiry details."""
        return [self.__details(link) for link in self.links.owned_by(created_by)]

    def short_url(self, dst: str) -> HttpUrl:
        """Build the public URL for a short code."""
        return HttpUrl(f"{self.public_url}/{dst}")

    def delete(self, dst: str, created_by: str) -> None:
        """Delete a user's link and its QR code, if present."""
        link = self.__owned(dst, created_by)
        self.links.delete(link.dst)
        if link.connected_to is not None:
            self.__delete_qr(link.connected_to)

    def create_qr(self, dst: str, created_by: str) -> None:
        """Create and store a QR code for a user's link."""
        link = self.__owned(dst, created_by)
        if link.connected_to is not None:
            return

        key = f"qr/{link.dst}-{secrets.token_hex(4)}.png"
        try:
            self.storage.put(key, self.__render(self.short_url(link.dst)), "image/png")
        except StorageUnavailable as e:
            raise QrUnavailable from e

        try:
            qr = self.qr_codes.add(NewQrCode(storage_key=key, created_by=created_by))
            connected = self.links.connect(link.dst, qr.id)
        except Exception:
            self.__discard(key)
            raise
        if not connected:
            self.__delete_qr(qr.id)

    def __validate(
        self, src: str, dst: str | None, expires_in_days: str | int | None
    ) -> ShortenRequest:
        """Validate link input and translate field errors."""
        try:
            return ShortenRequest.model_validate(
                {"src": src, "dst": dst, "expires_in_days": expires_in_days}
            )
        except ValidationError as e:
            field = str(e.errors()[0]["loc"][0])
            raise FIELD_ERRORS.get(field, InvalidLink)() from e

    def __owned(self, dst: str, created_by: str) -> Link:
        """Find the user's link or raise LinkNotFound."""
        link = self.links.get(dst)
        if link is None or link.created_by != created_by:
            raise LinkNotFound
        return link

    def __details(self, link: Link) -> LinkDetails:
        """Build display details for a link."""
        return LinkDetails(
            link=link,
            short_url=self.short_url(link.dst),
            qr_url=self.__qr_url(link),
            expired=self.__is_expired(link),
        )

    def __qr_url(self, link: Link) -> HttpUrl | None:
        """Get a signed URL for the QR image, if available."""
        if link.connected_to is None:
            return None
        qr = self.qr_codes.get(link.connected_to)
        if qr is None:
            return None
        try:
            return self.storage.get(qr.storage_key, QR_URL_LIFETIME)
        except StorageUnavailable:
            logger.exception("Could not sign QR code %s", qr.storage_key)
            return None

    def __delete_qr(self, qr_id: int) -> None:
        """Delete a QR record and discard its stored image."""
        qr = self.qr_codes.get(qr_id)
        if qr is None:
            return
        self.qr_codes.delete(qr.id)
        self.__discard(qr.storage_key)

    def __discard(self, key: str) -> None:
        """Try to delete a stored image and log failures."""
        try:
            self.storage.delete(key)
        except StorageUnavailable:
            logger.exception("Could not delete stored object %s", key)

    def __render(self, url: HttpUrl) -> io.BytesIO:
        """Create a PNG QR image for the URL."""
        image = io.BytesIO()
        qrcode.make(str(url)).save(image)
        image.seek(0)
        return image

    def __is_expired(self, link: Link) -> bool:
        """Check if the link has expired."""
        return link.expires_at is not None and link.expires_at <= datetime.now(UTC)

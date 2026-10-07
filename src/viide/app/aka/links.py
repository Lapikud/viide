"""Short link models and their repository port.

``src`` is the target URL and ``dst`` is the short code.
"""

from datetime import datetime
from typing import Annotated, Any, Protocol

from pydantic import (
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    PlainSerializer,
    StringConstraints,
)


def blank_to_none(value: Any) -> Any:
    """Convert blank strings to None before validation."""
    return (value.strip() or None) if isinstance(value, str) else value


type ShortCode = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,255}$")]
type Url = Annotated[HttpUrl, PlainSerializer(str)]
type Days = Annotated[int, Field(gt=0, le=3650)]


class ShortenRequest(BaseModel):
    """Validate input for a new short link."""

    src: Url
    dst: Annotated[ShortCode | None, BeforeValidator(blank_to_none)] = None
    expires_in_days: Annotated[Days | None, BeforeValidator(blank_to_none)] = None


class NewLink(BaseModel):
    """Hold link data before it is saved."""

    model_config = ConfigDict(frozen=True, from_attributes=True)

    src: Url
    dst: ShortCode
    created_by: str
    expires_at: AwareDatetime | None = None
    static: bool = False


class Link(NewLink):
    """Hold a saved link and its QR connection."""

    created_at: datetime
    connected_to: int | None


class LinkDetails(BaseModel):
    """Hold a link and the URLs shown to its owner."""

    model_config = ConfigDict(frozen=True)

    link: Link
    short_url: HttpUrl
    qr_url: HttpUrl | None
    expired: bool


class LinkRepository(Protocol):
    """Define how links are saved and retrieved."""

    def add(self, link: NewLink) -> Link:
        """Store a new link and return it."""
        ...

    def get(self, dst: str) -> Link | None:
        """Find a link by its short code."""
        ...

    def owned_by(self, created_by: str) -> list[Link]:
        """List links created by the user."""
        ...

    def connect(self, dst: str, qr_id: int) -> bool:
        """Attach a QR code to an unconnected link."""
        ...

    def delete(self, dst: str) -> None:
        """Remove a link by its short code."""
        ...

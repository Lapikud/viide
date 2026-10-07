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
    return (value.strip() or None) if isinstance(value, str) else value


type ShortCode = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,255}$")]
type Url = Annotated[HttpUrl, PlainSerializer(str)]
type Days = Annotated[int, Field(gt=0, le=3650)]


class ShortenRequest(BaseModel):
    src: Url
    dst: Annotated[ShortCode | None, BeforeValidator(blank_to_none)] = None
    expires_in_days: Annotated[Days | None, BeforeValidator(blank_to_none)] = None


class NewLink(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    src: Url
    dst: ShortCode
    created_by: str
    expires_at: AwareDatetime | None = None
    static: bool = False


class Link(NewLink):
    created_at: datetime
    connected_to: int | None


class LinkDetails(BaseModel):
    model_config = ConfigDict(frozen=True)

    link: Link
    short_url: HttpUrl
    qr_url: HttpUrl | None
    expired: bool


class LinkRepository(Protocol):
    def add(self, link: NewLink) -> Link: ...

    def get(self, dst: str) -> Link | None: ...

    def owned_by(self, created_by: str) -> list[Link]: ...

    def connect(self, dst: str, qr_id: int) -> bool: ...

    def delete(self, dst: str) -> None: ...

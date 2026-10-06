from datetime import datetime
from typing import Annotated, Protocol

from pydantic import BaseModel, ConfigDict, HttpUrl, PlainSerializer, StringConstraints

type ShortCode = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,255}$")]
type Url = Annotated[HttpUrl, PlainSerializer(str)]


class NewLink(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    src: Url
    dst: ShortCode
    created_by: str
    expires_at: datetime | None = None


class Link(NewLink):
    created_at: datetime
    connected_to: int | None


class LinkRepository(Protocol):
    def add(self, link: NewLink) -> Link: ...

    def get(self, dst: str) -> Link | None: ...

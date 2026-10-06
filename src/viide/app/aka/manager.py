import secrets
from datetime import UTC, datetime

from pydantic import ValidationError

from .errors import InvalidLink, LinkNotFound, ShortCodeTaken
from .links import Link, LinkRepository, NewLink

ATTEMPTS = 5


class LinkManager:
    def __init__(self, links: LinkRepository) -> None:
        self.links = links

    def shorten(
        self, src: str, created_by: str, dst: str | None = None, expires_at: datetime | None = None
    ) -> Link:
        if dst:
            return self.links.add(self.__new_link(src, dst, created_by, expires_at))

        for _ in range(ATTEMPTS):
            try:
                return self.links.add(
                    self.__new_link(src, secrets.token_urlsafe(5), created_by, expires_at)
                )
            except ShortCodeTaken:
                continue
        raise ShortCodeTaken

    def resolve(self, dst: str) -> Link:
        link = self.links.get(dst)
        if link is None or (link.expires_at is not None and link.expires_at <= datetime.now(UTC)):
            raise LinkNotFound
        return link

    def __new_link(
        self, src: str, dst: str, created_by: str, expires_at: datetime | None
    ) -> NewLink:
        try:
            return NewLink.model_validate(
                {"src": src, "dst": dst, "created_by": created_by, "expires_at": expires_at}
            )
        except ValidationError as e:
            raise InvalidLink from e

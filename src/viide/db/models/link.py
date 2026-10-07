"""The ``links`` table, which holds every short link."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from viide.db.base import Base


class Link(Base):
    """Map a short link to the links table."""

    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    src: Mapped[str] = mapped_column(Text)
    dst: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    connected_to: Mapped[int | None] = mapped_column(
        ForeignKey("qr_codes.id", ondelete="SET NULL"), index=True
    )
    created_by: Mapped[str] = mapped_column(String(255), index=True)

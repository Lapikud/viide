"""The declarative base for all models, with stable names for migrations."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Apply shared naming rules to SQLAlchemy models."""

    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ck": "chk_%(table_name)s_%(column_0_name)s",
            "ix": "idx_%(table_name)s_%(column_0_name)s",
        }
    )

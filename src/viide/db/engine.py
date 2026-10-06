from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from viide.config import Settings


def create_db(settings: Settings) -> sessionmaker[Session]:
    return sessionmaker(
        bind=create_engine(str(settings.database_url)), expire_on_commit=False
    )

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Determine which database URL to use
database_url = settings.get_database_url()

# Configure connection arguments based on database type
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        database_url,
        pool_size=settings.db_pool_size,  # Minimum 5 connections
        max_overflow=settings.db_max_overflow,  # Maximum 20 total (5 + 15)
        pool_timeout=settings.db_pool_timeout,  # 30 seconds timeout
        pool_recycle=settings.db_pool_recycle,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Verify connections before using them
        echo=settings.debug,  # Log SQL queries in debug mode
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


if database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

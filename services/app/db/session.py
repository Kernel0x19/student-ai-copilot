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
    _run_migrations()


def _run_migrations() -> None:
    """Apply additive schema migrations that create_all cannot handle."""
    with engine.connect() as conn:
        # Add backlogs column to student_profiles if it doesn't exist yet
        if database_url.startswith("sqlite"):
            from sqlalchemy import text
            cols = [
                row[1] for row in conn.execute(
                    text("PRAGMA table_info(student_profiles)")
                )
            ]
            if "backlogs" not in cols:
                conn.execute(text(
                    "ALTER TABLE student_profiles ADD COLUMN backlogs INTEGER"
                ))
                conn.commit()
        else:
            # PostgreSQL — use DO $$ ... $$ block
            from sqlalchemy import text
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='student_profiles' AND column_name='backlogs'
                    ) THEN
                        ALTER TABLE student_profiles ADD COLUMN backlogs INTEGER;
                    END IF;
                END $$;
            """))
            conn.commit()

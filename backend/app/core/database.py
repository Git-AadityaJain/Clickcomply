"""
Database engine and session management.

Uses SQLAlchemy async engine with aiosqlite for local development.
Replace the DATABASE_URL in config.py with a PostgreSQL URI for production.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Async engine — echo=True in debug mode for query logging
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Session factory — expires_on_commit=False so objects remain usable after commit
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


# Columns added after initial schema — migrate existing SQLite DBs in place
_DOCUMENT_FILE_COLUMNS: dict[str, str] = {
    "file_size": "INTEGER",
    "upload_timestamp": "DATETIME",
    "uploader_ip": "VARCHAR(45)",
    "original_filename": "VARCHAR(255)",
    "stored_filename": "VARCHAR(255)",
    "extracted_text": "TEXT",
}

_ANALYSIS_COLUMNS: dict[str, str] = {
    "result_json": "TEXT",
}


async def _migrate_sqlite_schema(conn) -> None:
    """Add columns introduced after initial deployments."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    result = await conn.execute(text("PRAGMA table_info(documents)"))
    doc_columns = {row[1] for row in result.fetchall()}

    for column, col_type in _DOCUMENT_FILE_COLUMNS.items():
        if column not in doc_columns:
            await conn.execute(
                text(f"ALTER TABLE documents ADD COLUMN {column} {col_type}")
            )

    result = await conn.execute(text("PRAGMA table_info(analysis_results)"))
    analysis_columns = {row[1] for row in result.fetchall()}

    for column, col_type in _ANALYSIS_COLUMNS.items():
        if column not in analysis_columns:
            await conn.execute(
                text(f"ALTER TABLE analysis_results ADD COLUMN {column} {col_type}")
            )


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields a database session.
    Automatically closes the session when the request is complete.
    """
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """
    Creates all database tables on application startup.
    Called from the FastAPI lifespan handler in main.py.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate_sqlite_schema(conn)

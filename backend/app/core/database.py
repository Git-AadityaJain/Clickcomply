"""
Database engine and session management.

Uses SQLAlchemy async engine with aiosqlite for local development.
Replace the DATABASE_URL in config.py with a PostgreSQL URI for production.
"""

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

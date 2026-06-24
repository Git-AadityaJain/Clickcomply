"""
Application configuration module.

Centralizes all environment-based and static configuration values
used throughout the ClickComply backend.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# backend/ — stable base for DB and uploads regardless of process cwd
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Global application settings sourced from environment variables."""

    # Application metadata
    APP_NAME: str = "ClickComply"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "AI-powered DPDP Act compliance platform. "
        "AI analysis engine is not yet integrated — architecture is ready for RAG+LLM."
    )

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database — defaults to SQLite for local development.
    # Switch to a PostgreSQL connection string for production.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{(_BACKEND_ROOT / 'clickcomply.db').as_posix()}",
    )

    # CORS — allowed origins for the frontend
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # File upload settings
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        str(_BACKEND_ROOT / "uploads"),
    )
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50 MB default


settings = Settings()

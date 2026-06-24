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
        "AI-powered DPDP Act compliance platform with local RAG + Ollama analysis."
    )

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database — defaults to SQLite for local development.
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
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50 MB

    # AI / RAG — default: Ollama (free, runs locally; no API keys)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama").lower()  # ollama | openai | gemini

    # Ollama (free local — recommended)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))

    # Optional paid cloud providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "models/text-embedding-004"
    )
    AI_MAX_DOCUMENT_CHARS: int = int(os.getenv("AI_MAX_DOCUMENT_CHARS", "12000"))
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "900"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
    RAG_TOP_K_DPDP: int = int(os.getenv("RAG_TOP_K_DPDP", "3"))
    RAG_TOP_K_DOCUMENT: int = int(os.getenv("RAG_TOP_K_DOCUMENT", "5"))
    CHROMA_DIR: Path = Path(
        os.getenv("CHROMA_DIR", str(_BACKEND_ROOT / "chroma_data"))
    )


settings = Settings()

"""
Application configuration module.

Centralizes all environment-based and static configuration values
used throughout the ClickComply backend.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# backend/: stable base for DB and uploads regardless of process cwd
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

    # Ephemeral uploads are pruned via POST /documents/prune-session (browser refresh).
    # Optional shutdown wipe for deployments that want a clean server stop.
    CLEAR_EPHEMERAL_ON_SHUTDOWN: bool = (
        os.getenv("CLEAR_EPHEMERAL_ON_SHUTDOWN", "false").lower() == "true"
    )

    # Database: defaults to SQLite for local development.
    # For production set e.g.
    #   DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/clickcomply
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{(_BACKEND_ROOT / 'clickcomply.db').as_posix()}",
    )

    @property
    def IS_SQLITE(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    # CORS: allowed origins for the frontend. Override via comma-separated
    # CORS_ORIGINS env var in production.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    # Auth / security (Phase 2)
    # REQUIRE_AUTH=false keeps the open local-dev workflow (documents are not
    # user-scoped); set true in staging/prod to force login on every route.
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-insecure-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TTL_MINUTES: int = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))
    JWT_REFRESH_TTL_DAYS: int = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))

    # File upload settings
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        str(_BACKEND_ROOT / "uploads"),
    )
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50 MB

    # AI / RAG: default Ollama (free, runs locally; no API keys)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama").lower()  # ollama | openai | gemini

    # Ollama (free local, recommended)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "360"))

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
    # Full document text is always injected into every rule prompt up to
    # AI_MAX_DOCUMENT_CHARS. For documents larger than this limit, the text
    # is split: the first AI_MAX_DOC_HEAD_CHARS chars + the last
    # AI_MAX_DOC_TAIL_CHARS chars are always included (capturing intro and
    # contact/grievance sections), and RAG retrieval adds the most relevant
    # middle chunks on top. This ensures strict, equal treatment at every size.
    AI_MAX_DOCUMENT_CHARS: int = int(os.getenv("AI_MAX_DOCUMENT_CHARS", "32000"))
    AI_MAX_DOC_HEAD_CHARS: int = int(os.getenv("AI_MAX_DOC_HEAD_CHARS", "14000"))
    AI_MAX_DOC_TAIL_CHARS: int = int(os.getenv("AI_MAX_DOC_TAIL_CHARS", "8000"))
    AI_MAX_RAG_SUPPLEMENT_CHARS: int = int(os.getenv("AI_MAX_RAG_SUPPLEMENT_CHARS", "6000"))
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
    RAG_TOP_K_DPDP: int = int(os.getenv("RAG_TOP_K_DPDP", "4"))
    RAG_TOP_K_DOCUMENT: int = int(os.getenv("RAG_TOP_K_DOCUMENT", "8"))
    CHROMA_DIR: Path = Path(
        os.getenv("CHROMA_DIR", str(_BACKEND_ROOT / "chroma_data"))
    )


settings = Settings()

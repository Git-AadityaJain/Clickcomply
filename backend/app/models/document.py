"""
SQLAlchemy ORM model for the `documents` table.

Stores metadata about policy / compliance documents uploaded by the admin.
Actual file content is NOT stored — this table records ingestion metadata only.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    """
    Represents a compliance document tracked by the system.

    Lifecycle statuses:
        RECEIVED              — Document metadata accepted by the API.
        QUEUED_FOR_ANALYSIS   — Queued for the AI compliance engine (not yet active).
        AWAITING_AI_ANALYSIS  — Waiting for AI processing (placeholder state).
        ANALYSIS_COMPLETE     — Analysis finished (future state).
    """

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="RECEIVED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    # File upload metadata
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upload_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    uploader_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stored_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # One-to-many relationship with analysis results
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} name={self.document_name} status={self.status}>"

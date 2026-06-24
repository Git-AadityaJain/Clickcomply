"""
SQLAlchemy ORM model for the `analysis_results` table.

Stores persisted output of RAG+LLM compliance analysis runs.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisResult(Base):
    """
    Represents a single compliance analysis run for a document.

    `result_json` holds the full ComplianceAnalysisResponse payload.
    `summary` stores the human-readable note from the analysis.
    """

    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING_AI_REVIEW",
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Back-reference to the parent document
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="analysis_results",
    )

    def __repr__(self) -> str:
        return f"<AnalysisResult id={self.id} doc={self.document_id} status={self.analysis_status}>"

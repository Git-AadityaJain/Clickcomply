"""
SQLAlchemy ORM model for the `analysis_results` table.

Stores the output of compliance analysis runs against uploaded documents.
Currently populated with placeholder data; will contain real AI output
once the RAG+LLM engine is integrated.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisResult(Base):
    """
    Represents a single compliance analysis run for a document.

    The `summary` field is nullable — it will be populated by the
    AI engine once integrated. Until then, the placeholder service
    returns a static response without persisting a summary.
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

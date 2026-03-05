"""
Pydantic schemas for document-related request and response payloads.

These schemas define the API contract and remain stable even after
the AI engine is integrated — only internal service logic will change.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    """Request body for POST /documents/ingest."""

    document_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the document being ingested (e.g. privacy_policy.pdf).",
        examples=["privacy_policy.pdf"],
    )
    document_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category of the document (e.g. privacy_policy, terms_of_service).",
        examples=["privacy_policy"],
    )


class DocumentIngestResponse(BaseModel):
    """Response body for POST /documents/ingest."""

    document_id: str
    status: str
    message: str


class DocumentStatusResponse(BaseModel):
    """Response body for GET /documents/{document_id}/status."""

    document_id: str
    status: str


class DocumentListItem(BaseModel):
    """Single document entry returned in list endpoints."""

    id: str
    document_name: str
    document_type: str
    status: str
    created_at: datetime
    file_size: int | None = None
    upload_timestamp: datetime | None = None
    uploader_ip: str | None = None
    original_filename: str | None = None
    stored_filename: str | None = None

    model_config = {"from_attributes": True}

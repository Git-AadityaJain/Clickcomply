"""
Document-related Pydantic schemas.
"""

from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.org_profile import ApplicabilityReport, OrgProfile


class DocumentIngestRequest(BaseModel):
    """Request body for POST /documents/ingest."""

    org_profile: OrgProfile
    document_name: str | None = Field(
        default=None,
        max_length=255,
        description="Optional; defaults to {legal_name} privacy policy.",
    )
    document_type: str = Field(
        default="privacy_policy",
        min_length=1,
        max_length=100,
    )


class DocumentIngestResponse(BaseModel):
    document_id: str
    status: str
    message: str
    generated_policy_available: bool = False
    applicability: ApplicabilityReport | None = None


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str


class DocumentListItem(BaseModel):
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
    remember: bool = False
    has_org_profile: bool = False
    has_generated_policy: bool = False
    has_uploaded_file: bool = False

    model_config = {"from_attributes": True}


class DocumentRememberUpdate(BaseModel):
    remember: bool = Field(..., description="Keep document across server restarts")


class GeneratePolicyRequest(BaseModel):
    format: Literal["docx", "pdf"] = "docx"


class GeneratePolicyResponse(BaseModel):
    document_id: str
    format: str
    filename: str
    legal_name: str


class ApplicabilityResponse(BaseModel):
    document_id: str
    report: ApplicabilityReport


class PruneSessionRequest(BaseModel):
    keep_document_ids: list[str] = Field(
        default_factory=list,
        description="Document IDs marked to keep in the browser before pruning",
    )


class PruneSessionResponse(BaseModel):
    removed_count: int
    removed_ids: list[str]

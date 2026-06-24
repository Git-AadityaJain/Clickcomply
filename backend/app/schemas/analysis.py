"""
Pydantic schemas for compliance analysis request and response payloads.
"""

from pydantic import BaseModel, Field


class ComplianceGap(BaseModel):
    """A single identified compliance gap."""

    section: str
    description: str
    severity: str  # e.g. "HIGH", "MEDIUM", "LOW"


class Recommendation(BaseModel):
    """A single actionable compliance recommendation."""

    section: str
    action: str
    priority: str  # e.g. "CRITICAL", "HIGH", "MEDIUM", "LOW"


class AnalysisProgress(BaseModel):
    """Rule-by-rule progress while analysis is running."""

    current: int
    total: int
    rule_id: str
    rule_label: str


class ComplianceAnalysisResponse(BaseModel):
    """Response body for GET /analysis/{document_id}."""

    overall_status: str
    identified_gaps: list[ComplianceGap]
    recommendations: list[Recommendation]
    note: str
    progress: AnalysisProgress | None = None
    rules_evaluated: int | None = Field(
        default=None,
        description="Number of DPDP rules evaluated (present when analysis is complete).",
    )


class AnalysisRerunResponse(BaseModel):
    """Response body for POST /analysis/{document_id}/rerun."""

    document_id: str
    status: str
    message: str

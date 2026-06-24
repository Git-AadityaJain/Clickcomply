"""
Pydantic schemas for compliance analysis request and response payloads.
"""

from pydantic import BaseModel, Field

from app.schemas.org_profile import ApplicabilityReport


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


class PolicyComparison(BaseModel):
    """Comparison of uploaded policy vs generated ideal draft."""

    summary: str
    missing_in_upload: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


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
    skipped_rules: list[str] | None = Field(
        default=None,
        description="Rule IDs skipped as not applicable to declared processing.",
    )
    applicability_report: ApplicabilityReport | None = None
    policy_comparison: PolicyComparison | None = None


class AnalysisRerunResponse(BaseModel):
    """Response body for POST /analysis/{document_id}/rerun."""

    document_id: str
    status: str
    message: str


class AnalysisCancelResponse(BaseModel):
    """Response body for POST /analysis/{document_id}/cancel."""

    document_id: str
    status: str
    message: str

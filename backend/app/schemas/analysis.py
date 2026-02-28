"""
Pydantic schemas for compliance analysis request and response payloads.

The response structure is designed to remain stable after AI integration.
The `identified_gaps` and `recommendations` lists will be populated by
the AI engine; until then they are returned empty with a status note.
"""

from pydantic import BaseModel


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


class ComplianceAnalysisResponse(BaseModel):
    """
    Response body for GET /analysis/{document_id}.

    This schema is the contract between frontend and backend.
    It will NOT change when AI is integrated — only the data
    populating it will become dynamic instead of static.
    """

    overall_status: str
    identified_gaps: list[ComplianceGap]
    recommendations: list[Recommendation]
    note: str

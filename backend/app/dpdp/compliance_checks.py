"""
Compliance check orchestration — delegates to the RAG+LLM analysis pipeline.

Per-rule evaluation is performed inside ai_service.run_compliance_analysis().
This module exposes helpers for future granular check APIs.
"""

from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES


async def run_all_checks(document_id: str) -> list[dict]:
    """
    Return compliance check summaries for a document.

    Full evaluation runs in ai_service during upload-triggered analysis.
    """
    logger.info(f"Compliance check summary requested for document {document_id}")

    return [
        {
            "rule_id": rule["rule_id"],
            "section_ref": rule["section_ref"],
            "description": rule["description"],
            "severity": rule["severity"],
            "result": "SEE_ANALYSIS",
            "detail": "Use GET /analysis/{document_id} for RAG+LLM results.",
        }
        for rule in COMPLIANCE_RULES
    ]

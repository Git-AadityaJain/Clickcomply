"""
Compliance check stubs for the DPDP Act.

These functions define the interface for per-section compliance evaluation.
Currently they return placeholder results. When the AI engine is integrated,
each function will receive document content and use the LLM to evaluate
compliance against the specific DPDP section.

Integration plan:
    1. Each check function receives the extracted document text.
    2. The function constructs a section-specific prompt using the
       `ai_prompt_hint` from dpdp_rules.py.
    3. The LLM returns a structured evaluation (PASS / FAIL / NEEDS_REVIEW).
    4. Results are aggregated by the analysis_service.
"""

from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES


async def run_all_checks(document_id: str) -> list[dict]:
    """
    Run all DPDP compliance checks against a document.

    Currently returns PENDING for every rule. When AI is connected,
    this function will iterate over COMPLIANCE_RULES and invoke
    section-specific evaluation for each.

    Args:
        document_id: UUID of the document being evaluated.

    Returns:
        List of check result dictionaries.
    """
    logger.info(f"Running compliance checks for document {document_id}")

    results = []
    for rule in COMPLIANCE_RULES:
        # Stub: every check returns PENDING until AI is integrated
        results.append({
            "rule_id": rule["rule_id"],
            "section_ref": rule["section_ref"],
            "description": rule["description"],
            "severity": rule["severity"],
            "result": "PENDING",  # Will be PASS / FAIL / NEEDS_REVIEW
            "detail": "AI compliance engine not yet integrated.",
        })

    logger.info(f"Completed {len(results)} checks for document {document_id} (all PENDING)")

    return results


async def check_consent(document_text: str) -> dict:
    """
    Evaluate document against DPDP Section 6 — Consent requirements.

    Args:
        document_text: Extracted text content of the document.

    Returns:
        Check result with status and detail.
    """
    # TODO: Replace with LLM-based evaluation using consent-specific prompt
    return {"result": "PENDING", "detail": "Consent check awaiting AI integration."}


async def check_notice(document_text: str) -> dict:
    """
    Evaluate document against DPDP Section 5 — Notice requirements.

    Args:
        document_text: Extracted text content of the document.

    Returns:
        Check result with status and detail.
    """
    # TODO: Replace with LLM-based evaluation using notice-specific prompt
    return {"result": "PENDING", "detail": "Notice check awaiting AI integration."}


async def check_child_data(document_text: str) -> dict:
    """
    Evaluate document against DPDP Section 9 — Child data protections.

    Args:
        document_text: Extracted text content of the document.

    Returns:
        Check result with status and detail.
    """
    # TODO: Replace with LLM-based evaluation using child data prompt
    return {"result": "PENDING", "detail": "Child data check awaiting AI integration."}


async def check_breach_notification(document_text: str) -> dict:
    """
    Evaluate document against DPDP Section 8(6) — Breach notification.

    Args:
        document_text: Extracted text content of the document.

    Returns:
        Check result with status and detail.
    """
    # TODO: Replace with LLM-based evaluation using breach notification prompt
    return {"result": "PENDING", "detail": "Breach notification check awaiting AI integration."}

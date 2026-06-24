"""
AI compliance analysis engine — RAG + LLM evaluation against DPDP rules.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.services.document_service import get_document_by_id
from app.services.llm_client import (
    LLMConfigurationError,
    active_chat_model,
    complete_json,
    get_ai_setup_hint,
    is_ai_configured,
)
from app.services.rag_service import index_document_text, query_document_context, query_dpdp_context
from app.services.text_extractor import TextExtractionError, extract_text_from_path


SYSTEM_PROMPT = """You are an expert auditor for India's Digital Personal Data Protection Act (DPDP) 2023.
Evaluate whether an uploaded policy document satisfies a specific compliance rule.
Use only the provided DPDP provisions and document excerpts.
Be precise and cite the rule section when identifying gaps.
Respond ONLY with valid JSON matching this schema:
{
  "result": "PASS" | "FAIL" | "NEEDS_REVIEW",
  "detail": "brief explanation",
  "gap_description": "specific gap if FAIL or NEEDS_REVIEW, else empty string",
  "recommendation": "actionable fix if FAIL or NEEDS_REVIEW, else empty string"
}"""


async def check_ai_health() -> dict:
    """Health check for the AI subsystem."""
    if not is_ai_configured():
        return {
            "ai_engine": settings.AI_PROVIDER,
            "status": "NOT_CONFIGURED",
            "message": get_ai_setup_hint(),
        }

    try:
        from app.services.rag_service import init_dpdp_knowledge_base

        init_dpdp_knowledge_base()
        return {
            "ai_engine": settings.AI_PROVIDER,
            "status": "READY",
            "message": f"RAG + {settings.AI_PROVIDER} analysis engine is ready.",
            "model": active_chat_model(),
        }
    except Exception as exc:
        logger.error(f"AI health check failed: {exc}")
        return {
            "ai_engine": settings.AI_PROVIDER,
            "status": "ERROR",
            "message": str(exc),
        }


async def run_compliance_analysis(document_id: str, db: AsyncSession) -> dict:
    """
    Run full DPDP compliance analysis for a document using RAG + LLM.

    Args:
        document_id: UUID of the document.
        db: Active database session.

    Returns:
        Dictionary matching ComplianceAnalysisResponse schema.
    """
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if not is_ai_configured():
        return _not_configured_response()

    text = await _resolve_document_text(document)
    if not text:
        return {
            "overall_status": "ANALYSIS_FAILED",
            "identified_gaps": [],
            "recommendations": [],
            "note": "No extractable text found in the uploaded document.",
        }

    try:
        index_document_text(document_id, text)
    except Exception as exc:
        logger.error(f"RAG indexing failed for {document_id}: {exc}")
        return {
            "overall_status": "ANALYSIS_FAILED",
            "identified_gaps": [],
            "recommendations": [],
            "note": f"Failed to index document for analysis: {exc}",
        }

    gaps: list[dict] = []
    recommendations: list[dict] = []
    needs_review = False
    failures = 0

    for rule in COMPLIANCE_RULES:
        try:
            evaluation = _evaluate_rule(rule, document_id)
        except LLMConfigurationError as exc:
            return {
                "overall_status": "ANALYSIS_FAILED",
                "identified_gaps": [],
                "recommendations": [],
                "note": str(exc),
            }
        except Exception as exc:
            logger.error(f"Rule {rule['rule_id']} evaluation failed: {exc}")
            needs_review = True
            gaps.append(
                {
                    "section": rule["section_ref"],
                    "description": f"Could not evaluate: {rule['description']} ({exc})",
                    "severity": rule["severity"],
                }
            )
            continue

        result = str(evaluation.get("result", "NEEDS_REVIEW")).upper()
        if result == "PASS":
            continue

        if result == "NEEDS_REVIEW":
            needs_review = True
        else:
            failures += 1

        gap_desc = evaluation.get("gap_description") or evaluation.get("detail") or rule["description"]
        gaps.append(
            {
                "section": rule["section_ref"],
                "description": gap_desc,
                "severity": rule["severity"],
            }
        )

        rec_action = evaluation.get("recommendation") or evaluation.get("detail")
        if rec_action:
            priority = "CRITICAL" if rule["severity"] == "HIGH" and result == "FAIL" else rule["severity"]
            recommendations.append(
                {
                    "section": rule["section_ref"],
                    "action": rec_action,
                    "priority": priority,
                }
            )

    if failures > 0:
        overall = "NON_COMPLIANT"
    elif needs_review or gaps:
        overall = "NEEDS_REVIEW"
    else:
        overall = "COMPLIANT"

    return {
        "overall_status": overall,
        "identified_gaps": gaps,
        "recommendations": recommendations,
        "note": (
            f"Analysis completed using {settings.AI_PROVIDER} with vector RAG over "
            f"{len(COMPLIANCE_RULES)} DPDP compliance rules."
        ),
    }


async def _resolve_document_text(document) -> str:
    """Load extracted text from DB or extract from disk."""
    if document.extracted_text and document.extracted_text.strip():
        return document.extracted_text.strip()

    if not document.stored_filename:
        return ""

    file_path = Path(settings.UPLOAD_DIR) / document.stored_filename
    if not file_path.exists():
        return ""

    try:
        return extract_text_from_path(file_path)
    except TextExtractionError as exc:
        logger.warning(f"Text extraction failed for {document.id}: {exc}")
        return ""


def _evaluate_rule(rule: dict, document_id: str) -> dict:
    """Evaluate a single compliance rule with RAG context."""
    query = f"{rule['description']} {rule['ai_prompt_hint']}"
    dpdp_context = query_dpdp_context(query)
    doc_context = query_document_context(document_id, query)

    truncated_doc = doc_context[: settings.AI_MAX_DOCUMENT_CHARS]

    user_prompt = f"""Compliance rule: {rule['rule_id']}
Section: {rule['section_ref']}
Requirement: {rule['description']}
Evaluation focus: {rule['ai_prompt_hint']}
Severity if non-compliant: {rule['severity']}

--- DPDP Act provisions (retrieved) ---
{dpdp_context}

--- Document excerpts (retrieved) ---
{truncated_doc}

Evaluate whether the document satisfies this rule."""

    return complete_json(SYSTEM_PROMPT, user_prompt)


def _not_configured_response() -> dict:
    return {
        "overall_status": "PENDING_AI_REVIEW",
        "identified_gaps": [],
        "recommendations": [],
        "note": (
            f"AI provider '{settings.AI_PROVIDER}' is not ready. {get_ai_setup_hint()}"
        ),
    }

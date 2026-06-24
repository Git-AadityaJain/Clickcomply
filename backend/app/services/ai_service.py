"""
AI compliance analysis engine: RAG + LLM evaluation against DPDP rules.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.dpdp.rule_applicability import (
    format_org_context,
    get_applicable_rules,
    RULE_PLAIN_LABELS,
)
from app.schemas.org_profile import ApplicabilityReport, ApplicabilityStatus
from app.services.document_service import get_document_by_id, parse_org_profile
from app.services.compare_service import compare_policies
from app.services.llm_client import (
    LLMConfigurationError,
    active_chat_model,
    complete_json,
    get_ai_setup_hint,
    is_ai_configured,
)
from app.services.rag_service import index_document_text, query_document_context, query_dpdp_context
from app.services.analysis_progress import (
    clear_analysis_progress,
    clear_cancel_request,
    is_cancel_requested,
    set_analysis_progress,
)
from app.services.text_extractor import TextExtractionError, extract_text_from_path


SYSTEM_PROMPT = """You are an expert auditor for India's Digital Personal Data Protection Act (DPDP) 2023.
Evaluate whether a policy document satisfies a specific compliance rule for the organization described.
Use only the provided DPDP provisions, organization processing profile, and document excerpts.
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
    Run tailored DPDP compliance analysis for a document using RAG + LLM.
    """
    document = await get_document_by_id(db, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    if not is_ai_configured():
        return _not_configured_response()

    profile = parse_org_profile(document)
    org_context = format_org_context(profile) if profile else ""

    applicability_report = _load_applicability(document)
    if profile:
        rules_to_evaluate = get_applicable_rules(profile)
    else:
        rules_to_evaluate = COMPLIANCE_RULES

    skipped_rule_ids = []
    if applicability_report:
        skipped_rule_ids = [
            r.rule_id
            for r in applicability_report.rules
            if r.status == ApplicabilityStatus.NOT_APPLICABLE
        ]

    text = await _resolve_document_text(document)
    if not text:
        return {
            "overall_status": "ANALYSIS_FAILED",
            "identified_gaps": [],
            "recommendations": [],
            "note": "No policy text found. Please upload your privacy policy (PDF or Word) first.",
            "skipped_rules": skipped_rule_ids,
            "applicability_report": applicability_report.model_dump() if applicability_report else None,
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
            "skipped_rules": skipped_rule_ids,
            "applicability_report": applicability_report.model_dump() if applicability_report else None,
        }

    gaps: list[dict] = []
    recommendations: list[dict] = []
    needs_review = False
    failures = 0
    total_rules = len(rules_to_evaluate)

    for index, rule in enumerate(rules_to_evaluate, start=1):
        if is_cancel_requested(document_id):
            clear_cancel_request(document_id)
            clear_analysis_progress(document_id)
            return {
                "overall_status": "ANALYSIS_CANCELLED",
                "identified_gaps": [],
                "recommendations": [],
                "note": "Analysis was stopped at your request.",
                "skipped_rules": skipped_rule_ids,
                "applicability_report": applicability_report.model_dump() if applicability_report else None,
            }

        set_analysis_progress(
            document_id,
            current=index,
            total=total_rules,
            rule_id=rule["rule_id"],
            rule_label=RULE_PLAIN_LABELS.get(rule["rule_id"], rule["description"]),
        )
        try:
            evaluation = _evaluate_rule(rule, document_id, org_context)
        except LLMConfigurationError as exc:
            clear_analysis_progress(document_id)
            return {
                "overall_status": "ANALYSIS_FAILED",
                "identified_gaps": [],
                "recommendations": [],
                "note": str(exc),
                "skipped_rules": skipped_rule_ids,
                "applicability_report": applicability_report.model_dump() if applicability_report else None,
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

    clear_analysis_progress(document_id)

    policy_comparison = None
    if document.stored_filename and document.generated_policy_md and org_context:
        comparison = compare_policies(text, document.generated_policy_md, org_context)
        policy_comparison = {
            "summary": comparison.get("summary", ""),
            "missing_in_upload": comparison.get("missing_in_upload", []),
            "contradictions": comparison.get("contradictions", []),
            "recommendations": comparison.get("recommendations", []),
        }

    skip_note = f" Skipped {len(skipped_rule_ids)} rules not applicable to declared processing." if skipped_rule_ids else ""

    return {
        "overall_status": overall,
        "identified_gaps": gaps,
        "recommendations": recommendations,
        "rules_evaluated": total_rules,
        "skipped_rules": skipped_rule_ids,
        "applicability_report": applicability_report.model_dump() if applicability_report else None,
        "policy_comparison": policy_comparison,
        "note": (
            f"Analysis completed using {settings.AI_PROVIDER} with vector RAG over "
            f"{total_rules} applicable DPDP rules (of {len(COMPLIANCE_RULES)} total).{skip_note}"
        ),
    }


def _load_applicability(document) -> ApplicabilityReport | None:
    if not document.applicability_json:
        return None
    try:
        return ApplicabilityReport.model_validate_json(document.applicability_json)
    except Exception:
        return None


async def _resolve_document_text(document) -> str:
    """Load extracted text from uploaded policy only."""
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


def _evaluate_rule(rule: dict, document_id: str, org_context: str) -> dict:
    """Evaluate a single compliance rule with RAG context and org profile."""
    query = f"{rule['description']} {rule['ai_prompt_hint']}"
    dpdp_context = query_dpdp_context(query)
    doc_context = query_document_context(document_id, query)

    truncated_doc = doc_context[: settings.AI_MAX_DOCUMENT_CHARS]

    org_block = f"\n--- Organization processing profile ---\n{org_context}\n" if org_context else ""

    user_prompt = f"""Compliance rule: {rule['rule_id']}
Section: {rule['section_ref']}
Requirement: {rule['description']}
Evaluation focus: {rule['ai_prompt_hint']}
Severity if non-compliant: {rule['severity']}
{org_block}
--- DPDP Act provisions (retrieved) ---
{dpdp_context}

--- Document excerpts (retrieved) ---
{truncated_doc}

Evaluate whether the document satisfies this rule for the organization's declared processing activities."""

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

"""
AI compliance analysis engine: RAG + LLM evaluation against DPDP rules.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.dpdp.dpdp_sections import DPDP_SECTIONS
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
from app.services.rag_service import index_document_text, query_document_context
from app.services.analysis_progress import (
    clear_analysis_progress,
    clear_cancel_request,
    is_cancel_requested,
    set_analysis_progress,
)
from app.services.text_extractor import TextExtractionError, extract_text_from_path


# Keywords are matched against section HEADINGS only (the first ## line of each section).
# Use specific phrases that appear in headings — NOT generic words like "contact" or
# "breach" that appear in every section body and would cause all sections to be selected.
_RULE_SECTION_KEYWORDS: dict[str, list[str]] = {
    "RULE_NOTICE_001":      ["data we collect", "notice", "overview", "scope", "section 5"],
    "RULE_CONSENT_001":     ["consent", "legal basis", "withdrawal", "section 6"],
    "RULE_LEGITIMATE_001":  ["legitimate", "legal basis", "without consent", "section 7"],
    "RULE_SECURITY_001":    ["security safeguard", "security measure", "section 8(5)", "rule 6"],
    "RULE_RETENTION_001":   ["retention", "erasure", "section 8(7)", "rule 8"],
    "RULE_RIGHTS_001":      ["your rights", "rights as a data principal", "section 11", "section 14"],
    "RULE_GRIEVANCE_001":   ["grievance", "section 8(10)", "section 13", "rule 14(3)"],
    "RULE_CONTACT_001":     ["designated contact", "section 8(9)", "rule 9", "dpo"],
    "RULE_BREACH_001":      ["breach notification", "data breach", "section 8(6)", "rule 7"],
    "RULE_TRANSFER_001":    ["cross-border", "transfer", "section 16", "storage location"],
    "RULE_VENDOR_001":      ["data processor", "third-party", "processor", "section 8 dpdp"],
    "RULE_SDF_001":         ["significant data fiduciary", "section 10", "sdf status"],
    "RULE_CHILD_001":       ["children", "persons under 18", "parental consent", "section 9"],
    "RULE_DISABILITY_001":  ["disability", "guardian authority", "section 9(1)", "rule 11"],
    "RULE_BOARD_001":       ["complaint to", "data protection board", "board of india"],
    "RULE_CONSENT_MGR_001": ["consent manager"],
}


def _extract_relevant_sections(full_doc_text: str, rule_id: str, max_chars: int = 6000) -> str:
    """
    Extract sections most relevant to the given rule by matching keywords against
    section HEADINGS only (the ## line). This prevents over-broad matching caused
    by common words like 'contact' or 'breach' appearing in every section body.

    Always includes the first section (title/intro) for context.
    Falls back to the first max_chars of the full document when no heading matches.
    """
    import re as _re

    keywords = _RULE_SECTION_KEYWORDS.get(rule_id, [])
    sections = _re.split(r"\n(?=##\s)", full_doc_text)

    if len(sections) <= 1:
        return full_doc_text[:max_chars]

    selected = [sections[0]]  # Always include title/intro section
    lower_kws = [k.lower() for k in keywords]

    for section in sections[1:]:
        # Match keywords against the heading line only, not the full body
        heading = section.split("\n", 1)[0].lower()
        if any(kw in heading for kw in lower_kws):
            selected.append(section)

    result = "\n\n".join(selected)

    # No headings matched — fall back to first max_chars of the full doc
    if len(selected) <= 1 or len(result) < 400:
        return full_doc_text[:max_chars]

    return result[:max_chars]


SYSTEM_PROMPT = """You are a strict compliance auditor for India's Digital Personal Data Protection Act (DPDP) 2023.
Evaluate whether a policy document satisfies a specific compliance rule for the organization described.
Apply the same rigorous standard regardless of document length — a long document receives no more leniency than a short one.

Rules for evaluation:
- PASS: the document explicitly and clearly addresses the requirement. Vague or implied coverage is NOT sufficient for PASS.
- FAIL: the document is silent on the requirement or contradicts it.
- NEEDS_REVIEW: the document partially addresses the requirement but is missing specific details (e.g., timeframes, named contacts, prescribed procedures).

Use only the provided DPDP provisions, organization processing profile, and document text.
Quote the exact policy text that satisfies or fails the rule in your detail field.
Respond ONLY with valid JSON matching this schema:
{
  "result": "PASS" | "FAIL" | "NEEDS_REVIEW",
  "detail": "brief explanation quoting relevant policy text",
  "gap_description": "specific missing element if FAIL or NEEDS_REVIEW, else empty string",
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

    if not await asyncio.to_thread(is_ai_configured):
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
    # #region agent log
    import json as _j_, time as _t_; from pathlib import Path as _P_; open(str(_P_(__file__).parent.parent.parent.parent / 'debug-db3a55.log'), 'a').write(_j_.dumps({"sessionId":"db3a55","runId":"run3","hypothesisId":"A+D","location":"ai_service.py:after_resolve_text","message":"resolved_doc_text","data":{"doc_id":document_id,"text_len":len(text),"text_empty":not bool(text),"first_200":text[:200] if text else "","last_200":text[-200:] if text else ""},"timestamp":int(_t_.time()*1000)}) + "\n")
    # #endregion
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
        # skip_if_indexed=True avoids re-embedding ~16 chunks on every re-run
        # when the document hasn't changed, saving ~8–12 s per analysis.
        await asyncio.to_thread(index_document_text, document_id, text, True)
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
            evaluation = await asyncio.to_thread(_evaluate_rule, rule, document_id, org_context, text)
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
        # #region agent log — capture LLM verdict for flagged rules
        _FLAGGED_R = {"RULE_GRIEVANCE_001", "RULE_CONTACT_001", "RULE_BREACH_001"}
        if rule["rule_id"] in _FLAGGED_R:
            import json as _j_, time as _t_; from pathlib import Path as _P_; open(str(_P_(__file__).parent.parent.parent.parent / 'debug-db3a55.log'), 'a').write(_j_.dumps({"sessionId":"db3a55","runId":"run3","hypothesisId":"C","location":"ai_service.py:llm_verdict","message":"llm_rule_result","data":{"rule_id":rule["rule_id"],"result":result,"detail":evaluation.get("detail","")[:300],"gap":evaluation.get("gap_description","")[:300]},"timestamp":int(_t_.time()*1000)}) + "\n")
        # #endregion
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

        # Always emit a recommendation for non-PASS rules; fall back to the
        # rule's built-in hint when the LLM returns no text (e.g. empty stub).
        rec_action = (
            evaluation.get("recommendation")
            or evaluation.get("detail")
            or rule.get("ai_prompt_hint")
            or f"Ensure your policy explicitly addresses: {rule['description']}"
        )
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
    """
    Load text to analyse: uploaded policy first, then generated draft as fallback.
    """
    if document.extracted_text and document.extracted_text.strip():
        return document.extracted_text.strip()

    if document.stored_filename:
        file_path = Path(settings.UPLOAD_DIR) / document.stored_filename
        if file_path.exists():
            try:
                return extract_text_from_path(file_path)
            except TextExtractionError as exc:
                logger.warning(f"Text extraction failed for {document.id}: {exc}")

    if document.generated_policy_md and document.generated_policy_md.strip():
        logger.info(
            f"No uploaded file for {document.id} — using generated draft as analysis source"
        )
        return document.generated_policy_md.strip()

    return ""


def _get_dpdp_context_for_rule(rule: dict) -> str:
    """
    Return relevant DPDP Act provisions for this rule by direct section lookup.

    This completely avoids an `embed_texts` HTTP call to Ollama per rule
    (saving ~2 s × 14 rules = ~28 s per analysis). The section_key on each
    rule maps directly to the right DPDP_SECTIONS entry, so the result is
    also more accurate than a semantic search.
    """
    parts: list[str] = []
    section_key = rule.get("section_key", "")
    if section_key and section_key in DPDP_SECTIONS:
        s = DPDP_SECTIONS[section_key]
        parts.append(f"{s['section']}: {s['title']}\n{s['description']}")
    if rule.get("ai_prompt_hint"):
        parts.append(rule["ai_prompt_hint"])
    return "\n\n".join(parts) if parts else rule.get("description", "")


def _evaluate_rule(
    rule: dict, document_id: str, org_context: str, full_doc_text: str = ""
) -> dict:
    """
    Evaluate a single compliance rule strictly and equally for all document sizes.

    Strategy: extract only the sections most relevant to this specific rule
    (intro + keyword-matched sections) rather than injecting the full document.
    Sending the full text to llama3.2 causes the 3B model to return empty
    stub responses because it is overwhelmed by the long prompt context.
    Focused sections keep the prompt under ~2,000–5,000 chars per rule call,
    which is within llama3.2's reliable reasoning range.
    """
    dpdp_context = _get_dpdp_context_for_rule(rule)

    if not full_doc_text:
        # No text available at all — pure RAG fallback
        rag_query = f"{rule['description']} {rule['ai_prompt_hint']}"
        doc_context = query_document_context(document_id, rag_query)
        doc_section = doc_context[: settings.AI_MAX_DOCUMENT_CHARS]
        doc_section_label = "Document excerpts (retrieved)"
        logger.debug(f"Rule {rule['rule_id']}: no full text — RAG only")
    else:
        # Extract only the sections most relevant to this rule.
        # Sending the entire document (even if it fits in the context window)
        # causes llama3.2 to return empty responses — the 3B model is overwhelmed
        # by long prompts and fails to produce meaningful JSON.
        # Cap at 6,000 chars: focused context the 3B model can reliably reason over.
        doc_section = _extract_relevant_sections(
            full_doc_text, rule["rule_id"], max_chars=6000
        )
        doc_section_label = "Relevant policy sections"
        logger.debug(
            f"Rule {rule['rule_id']}: section-extracted "
            f"({len(doc_section)} chars from {len(full_doc_text)} char doc)"
        )

    # #region agent log — log context details for the three flagged rules only
    _FLAGGED = {"RULE_GRIEVANCE_001", "RULE_CONTACT_001", "RULE_BREACH_001"}
    if rule["rule_id"] in _FLAGGED:
        import json as _j_, time as _t_; from pathlib import Path as _P_; open(str(_P_(__file__).parent.parent.parent.parent / 'debug-db3a55.log'), 'a').write(_j_.dumps({"sessionId":"db3a55","runId":"run3","hypothesisId":"F","location":"ai_service.py:evaluate_rule_context","message":"post_fix_context_snapshot","data":{"rule_id":rule["rule_id"],"full_doc_len":len(full_doc_text),"doc_section_len":len(doc_section),"doc_section_contains_72h":"72" in doc_section,"doc_section_contains_90d":"ninety" in doc_section.lower() or "90 day" in doc_section.lower(),"doc_section_contains_priya":"Priya" in doc_section,"doc_section_snippet":doc_section[:400]},"timestamp":int(_t_.time()*1000)}) + "\n")
    # #endregion

    org_block = (
        f"\n--- Organization processing profile ---\n{org_context}\n"
        if org_context
        else ""
    )

    user_prompt = f"""Compliance rule: {rule['rule_id']}
Section: {rule['section_ref']}
Requirement: {rule['description']}
Evaluation focus: {rule['ai_prompt_hint']}
Severity if non-compliant: {rule['severity']}
{org_block}
--- DPDP Act provisions (retrieved) ---
{dpdp_context}

--- {doc_section_label} ---
{doc_section}

Evaluate whether the document satisfies this rule for the organization's declared processing activities."""

    evaluation = complete_json(SYSTEM_PROMPT, user_prompt)

    # #region agent log — verdict after fix
    if rule["rule_id"] in _FLAGGED:
        import json as _j_, time as _t_; from pathlib import Path as _P_; open(str(_P_(__file__).parent.parent.parent.parent / 'debug-db3a55.log'), 'a').write(_j_.dumps({"sessionId":"db3a55","runId":"run3","hypothesisId":"F","location":"ai_service.py:llm_verdict_postfix","message":"post_fix_llm_result","data":{"rule_id":rule["rule_id"],"result":evaluation.get("result",""),"detail":evaluation.get("detail","")[:300],"gap":evaluation.get("gap_description","")[:300]},"timestamp":int(_t_.time()*1000)}) + "\n")
    # #endregion

    return evaluation


def _not_configured_response() -> dict:
    return {
        "overall_status": "PENDING_AI_REVIEW",
        "identified_gaps": [],
        "recommendations": [],
        "note": (
            f"AI provider '{settings.AI_PROVIDER}' is not ready. {get_ai_setup_hint()}"
        ),
    }

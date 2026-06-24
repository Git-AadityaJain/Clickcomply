"""
Compare uploaded policy text against generated ideal draft.
"""

from __future__ import annotations

from app.core.config import settings
from app.services.llm_client import complete_json, is_ai_configured


COMPARE_PROMPT = """You compare an organization's uploaded privacy policy against an ideal DPDP-aligned draft generated from their declared processing activities.
Identify missing sections, contradictions between declared activities and uploaded text, and material gaps.
Respond ONLY with valid JSON:
{
  "summary": "brief overall comparison",
  "missing_in_upload": ["item1", "item2"],
  "contradictions": ["item1"],
  "recommendations": ["item1"]
}"""


def compare_policies(uploaded_excerpt: str, generated_md: str, org_summary: str) -> dict:
    """Lightweight LLM comparison when both texts exist."""
    if not is_ai_configured():
        return {
            "summary": "AI not configured — comparison skipped.",
            "missing_in_upload": [],
            "contradictions": [],
            "recommendations": [],
        }

    uploaded = uploaded_excerpt[: settings.AI_MAX_DOCUMENT_CHARS // 2]
    generated = generated_md[: settings.AI_MAX_DOCUMENT_CHARS // 2]

    user_prompt = f"""Organization processing profile:
{org_summary}

--- Ideal generated draft (excerpt) ---
{generated}

--- Uploaded policy (excerpt) ---
{uploaded}

Compare the uploaded policy against the ideal draft and declared processing activities."""

    try:
        return complete_json(COMPARE_PROMPT, user_prompt)
    except Exception as exc:
        return {
            "summary": f"Comparison failed: {exc}",
            "missing_in_upload": [],
            "contradictions": [],
            "recommendations": [],
        }

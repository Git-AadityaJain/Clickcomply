"""
DPDP compliance rules definitions.

Each rule maps to a specific compliance obligation under the DPDP Act.
Rules are structured so the AI engine can iterate over them and
evaluate each against the content of an uploaded document.

When AI is integrated:
    - Each rule's `check_fn` key will reference an actual evaluation function.
    - The AI engine will score each rule as PASS / FAIL / NEEDS_REVIEW.
"""

from app.dpdp.dpdp_sections import DPDP_SECTIONS

# Compliance rules — each references a DPDP section and describes
# what the AI engine should check for in the document.
COMPLIANCE_RULES = [
    {
        "rule_id": "RULE_CONSENT_001",
        "section_key": "CONSENT",
        "section_ref": DPDP_SECTIONS["CONSENT"]["section"],
        "description": "Document must describe the mechanism for obtaining informed consent.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document describes how user consent is obtained, "
            "what information is provided before consent, and how consent "
            "can be withdrawn."
        ),
    },
    {
        "rule_id": "RULE_NOTICE_001",
        "section_key": "NOTICE",
        "section_ref": DPDP_SECTIONS["NOTICE"]["section"],
        "description": "Document must include a data processing notice with required details.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document includes a clear notice about what data "
            "is collected, the purpose of processing, and the Data Principal's rights."
        ),
    },
    {
        "rule_id": "RULE_PROCESSOR_001",
        "section_key": "PROCESSOR_DUTIES",
        "section_ref": DPDP_SECTIONS["PROCESSOR_DUTIES"]["section"],
        "description": "Document must outline data accuracy and safeguard measures.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check if the document describes measures to ensure data accuracy, "
            "completeness, and protection against unauthorized access."
        ),
    },
    {
        "rule_id": "RULE_CHILD_001",
        "section_key": "CHILD_DATA",
        "section_ref": DPDP_SECTIONS["CHILD_DATA"]["section"],
        "description": "Document must address special handling of children's personal data.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document addresses parental consent for minors, "
            "prohibits profiling/tracking children, and describes age verification."
        ),
    },
    {
        "rule_id": "RULE_RIGHTS_001",
        "section_key": "DATA_PRINCIPAL_RIGHTS",
        "section_ref": DPDP_SECTIONS["DATA_PRINCIPAL_RIGHTS"]["section"],
        "description": "Document must describe how Data Principals can exercise their rights.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check if the document explains how users can access, correct, "
            "or erase their data and how to nominate a representative."
        ),
    },
    {
        "rule_id": "RULE_BREACH_001",
        "section_key": "DATA_BREACH",
        "section_ref": DPDP_SECTIONS["DATA_BREACH"]["section"],
        "description": "Document must include a data breach notification procedure.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document describes the breach notification timeline, "
            "who is notified, and what information is communicated."
        ),
    },
    {
        "rule_id": "RULE_TRANSFER_001",
        "section_key": "CROSS_BORDER_TRANSFER",
        "section_ref": DPDP_SECTIONS["CROSS_BORDER_TRANSFER"]["section"],
        "description": "Document must address cross-border data transfer restrictions.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check if the document addresses whether personal data is transferred "
            "outside India and which safeguards are in place."
        ),
    },
]

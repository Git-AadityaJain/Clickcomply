"""
DPDP compliance rules definitions.

Each rule maps to Act 2023 obligations and, where applicable, DPDP Rules 2025.
The AI engine iterates over COMPLIANCE_RULES and evaluates each against
the uploaded document using RAG + LLM.
"""

from app.dpdp.dpdp_sections import DPDP_SECTIONS

COMPLIANCE_RULES = [
    {
        "rule_id": "RULE_NOTICE_001",
        "section_key": "NOTICE",
        "section_ref": DPDP_SECTIONS["NOTICE"]["section"],
        "description": "Document must include a DPDP-compliant notice with itemised data and purposes.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document provides clear notice in plain language with an itemised "
            "description of personal data collected, specified purpose(s), and goods/services enabled. "
            "Per DPDP Rules 2025 Rule 3, notice must also describe means to withdraw consent "
            "(with comparable ease), exercise rights, and contact the organisation. "
            "Check availability in English or Eighth Schedule languages where stated."
        ),
    },
    {
        "rule_id": "RULE_BOARD_001",
        "section_key": "BOARD_COMPLAINT",
        "section_ref": DPDP_SECTIONS["BOARD_COMPLAINT"]["section"],
        "description": "Document must explain how Data Principals may complain to the Data Protection Board.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check if the document informs Data Principals how to make a complaint to the "
            "Data Protection Board of India, as required by Section 5(1)(iii) and DPDP Rules 2025 Rule 3. "
            "Look for Board complaint process, link, or reference to prescribed manner."
        ),
    },
    {
        "rule_id": "RULE_CONSENT_001",
        "section_key": "CONSENT",
        "section_ref": DPDP_SECTIONS["CONSENT"]["section"],
        "description": "Document must describe the mechanism for obtaining informed consent.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if consent is described as free, specific, informed, and unambiguous with clear "
            "affirmative action. Verify withdrawal is as easy as giving consent, consequences of "
            "withdrawal are explained, and processing ceases within a reasonable time after withdrawal "
            "unless legally authorised otherwise."
        ),
    },
    {
        "rule_id": "RULE_CONSENT_MGR_001",
        "section_key": "CONSENT_MANAGER",
        "section_ref": DPDP_SECTIONS["CONSENT_MANAGER"]["section"],
        "description": "Document should address Consent Manager use where consent is managed via a registered platform.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "If the service uses or supports a Consent Manager, check whether the document explains "
            "how principals give, manage, review and withdraw consent through it, per Section 6(7)-(9) "
            "and DPDP Rules 2025 Rule 4. If not applicable, the document should state that consent "
            "is managed directly or that Consent Managers are not used."
        ),
    },
    {
        "rule_id": "RULE_LEGITIMATE_001",
        "section_key": "LEGITIMATE_USES",
        "section_ref": DPDP_SECTIONS["LEGITIMATE_USES"]["section"],
        "description": "Document must clarify when processing occurs without consent under legitimate uses.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check if the document explains any processing based on legitimate uses under Section 7 "
            "(e.g. state benefits, disaster safety, employment, medical emergency, legal compliance) "
            "and the conditions or limitations that apply."
        ),
    },
    {
        "rule_id": "RULE_SECURITY_001",
        "section_key": "PROCESSOR_DUTIES",
        "section_ref": DPDP_SECTIONS["PROCESSOR_DUTIES"]["section"],
        "description": "Document must describe reasonable security safeguards for personal data.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check if the document describes reasonable security safeguards per Section 8(5) and "
            "DPDP Rules 2025 Rule 6: encryption or equivalent protection, access controls, monitoring "
            "and logging for unauthorised access, backup/continuity measures, and organisational "
            "security practices. Also check data accuracy measures where decisions affect the principal."
        ),
    },
    {
        "rule_id": "RULE_RETENTION_001",
        "section_key": "DATA_RETENTION",
        "section_ref": DPDP_SECTIONS["DATA_RETENTION"]["section"],
        "description": "Document must define retention, inactivity erasure, and log retention periods.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check retention and erasure per Section 8(7)-(8) and DPDP Rules 2025 Rule 8: when data "
            "is deleted after consent withdrawal or purpose expiry; inactivity-based erasure and "
            "advance notice before deletion; minimum one-year retention of processing logs/traffic data "
            "where applicable; and legal retention exceptions."
        ),
    },
    {
        "rule_id": "RULE_CHILD_001",
        "section_key": "CHILD_DATA",
        "section_ref": DPDP_SECTIONS["CHILD_DATA"]["section"],
        "description": "Document must address children's data, verifiable parental consent, and advertising bans.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check Section 9 and DPDP Rules 2025 Rule 10: verifiable parental/guardian consent before "
            "processing children's data; prohibition of tracking, behavioural monitoring, and targeted "
            "advertising directed at children; no processing likely to cause detrimental effects on "
            "child well-being; and age verification or parental identification measures."
        ),
    },
    {
        "rule_id": "RULE_DISABILITY_001",
        "section_key": "DISABILITY_GUARDIAN",
        "section_ref": DPDP_SECTIONS["DISABILITY_GUARDIAN"]["section"],
        "description": "Document must address processing of data of persons with disability with lawful guardian.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check Section 9(1) and DPDP Rules 2025 Rule 11: if the service processes data of persons "
            "with disability who have a lawful guardian, whether verifiable guardian consent is described "
            "and how guardian authority is verified. If not applicable, document should state so."
        ),
    },
    {
        "rule_id": "RULE_RIGHTS_001",
        "section_key": "DATA_PRINCIPAL_RIGHTS",
        "section_ref": DPDP_SECTIONS["DATA_PRINCIPAL_RIGHTS"]["section"],
        "description": "Document must describe how Data Principals exercise access, correction, erasure, and nomination rights.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Sections 11-14 and DPDP Rules 2025 Rule 14: how to request access summaries, "
            "correction/completion/updating, erasure, information about processors data was shared with, "
            "means to exercise rights on website/app, and right to nominate someone upon death or incapacity."
        ),
    },
    {
        "rule_id": "RULE_GRIEVANCE_001",
        "section_key": "GRIEVANCE_REDRESSAL",
        "section_ref": DPDP_SECTIONS["GRIEVANCE_REDRESSAL"]["section"],
        "description": "Document must provide grievance redressal with prescribed response timelines.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Section 8(10), Section 13, and DPDP Rules 2025 Rule 14(3): readily available "
            "grievance mechanism, contact channel (DPO or grievance officer), and response within "
            "ninety days. Principals must exhaust grievance redressal before approaching the Board."
        ),
    },
    {
        "rule_id": "RULE_CONTACT_001",
        "section_key": "CONTACT_PUBLICATION",
        "section_ref": DPDP_SECTIONS["CONTACT_PUBLICATION"]["section"],
        "description": "Document must publish DPO or designated contact for processing questions.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Section 8(9) and DPDP Rules 2025 Rule 9: prominent publication of business contact "
            "information for the Data Protection Officer (if applicable) or a person who can answer "
            "questions about personal data processing on website, app, or policy document."
        ),
    },
    {
        "rule_id": "RULE_BREACH_001",
        "section_key": "DATA_BREACH",
        "section_ref": DPDP_SECTIONS["DATA_BREACH"]["section"],
        "description": "Document must include breach notification procedures including Board intimation within 72 hours.",
        "severity": "HIGH",
        "ai_prompt_hint": (
            "Check Section 8(6) and DPDP Rules 2025 Rule 7: procedures to notify affected Data Principals "
            "without delay with breach description, consequences, mitigation, and safety measures; "
            "and intimation to the Data Protection Board within seventy-two hours of becoming aware, "
            "with prescribed breach details and remedial measures."
        ),
    },
    {
        "rule_id": "RULE_TRANSFER_001",
        "section_key": "CROSS_BORDER_TRANSFER",
        "section_ref": DPDP_SECTIONS["CROSS_BORDER_TRANSFER"]["section"],
        "description": "Document must address cross-border data transfer restrictions and government requirements.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Section 16 and DPDP Rules 2025 Rule 15: whether personal data is transferred outside "
            "India, restricted countries, safeguards in place, and compliance with Central Government "
            "requirements on foreign access to data."
        ),
    },
    {
        "rule_id": "RULE_VENDOR_001",
        "section_key": "DATA_PROCESSOR",
        "section_ref": DPDP_SECTIONS["DATA_PROCESSOR"]["section"],
        "description": "Document must disclose third-party Data Processors and valid contractual engagement.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Section 8(1)-(2): disclosure of third-party Data Processors or sub-processors, purposes "
            "they serve, that processing occurs only under valid contract, fiduciary remains responsible "
            "for processor compliance, and contractual safeguards including security obligations."
        ),
    },
    {
        "rule_id": "RULE_SDF_001",
        "section_key": "SIGNIFICANT_DATA_FIDUCIARY",
        "section_ref": DPDP_SECTIONS["SIGNIFICANT_DATA_FIDUCIARY"]["section"],
        "description": "Document should address Significant Data Fiduciary obligations where applicable.",
        "severity": "MEDIUM",
        "ai_prompt_hint": (
            "Check Section 10 and DPDP Rules 2025 Rule 13: India-based DPO appointment, periodic DPIA "
            "and independent audit, algorithmic/technical measures not posing risk to principal rights, "
            "and restrictions on transfer of notified sensitive data outside India. If not an SDF, document "
            "should state applicability or that SDF obligations do not apply."
        ),
    },
]

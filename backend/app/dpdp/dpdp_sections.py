"""
DPDP Act (Digital Personal Data Protection Act, 2023): Section Definitions.

Key regulatory areas evaluated by the compliance engine. Each section maps to
one or more automated rules in `dpdp_rules.py`. DPDP Rules 2025 provisions
are indexed separately in `dpdp_rules_2025.py` for RAG retrieval.
"""

DPDP_SECTIONS = {
    "NOTICE": {
        "section": "Section 5",
        "title": "Notice",
        "description": (
            "Every Data Fiduciary must give notice to the Data Principal "
            "before or at the time of seeking consent, including how to "
            "exercise rights and complain to the Board."
        ),
    },
    "BOARD_COMPLAINT": {
        "section": "Section 5(1)(iii)",
        "title": "Complaint to Data Protection Board",
        "description": (
            "Notice must inform the Data Principal of the manner in which she "
            "may make a complaint to the Data Protection Board, as prescribed."
        ),
    },
    "CONSENT": {
        "section": "Section 6",
        "title": "Consent of Data Principal",
        "description": (
            "Requires free, specific, informed, unconditional and unambiguous consent "
            "with clear affirmative action. Consent may be managed via a Consent Manager."
        ),
    },
    "CONSENT_MANAGER": {
        "section": "Section 6(7)-(9)",
        "title": "Consent Manager",
        "description": (
            "Data Principals may give, manage, review or withdraw consent through a "
            "Consent Manager registered with the Board, accountable to the Data Principal."
        ),
    },
    "LEGITIMATE_USES": {
        "section": "Section 7",
        "title": "Certain Legitimate Uses",
        "description": (
            "Personal data may be processed without consent in specified circumstances "
            "(e.g. voluntary provision, state functions, employment, medical emergency, "
            "legal compliance) subject to applicable conditions."
        ),
    },
    "PROCESSOR_DUTIES": {
        "section": "Section 8",
        "title": "General Obligations of Data Fiduciary",
        "description": (
            "Data Fiduciary must ensure completeness, accuracy, and consistency "
            "of personal data, implement reasonable security safeguards, and remain "
            "responsible for processing by Data Processors."
        ),
    },
    "DATA_PROCESSOR": {
        "section": "Section 8(1)-(2)",
        "title": "Data Processor Engagement",
        "description": (
            "Data Fiduciary remains responsible for compliance when using Data Processors. "
            "Processors may only be engaged under a valid contract for offering goods or services."
        ),
    },
    "DATA_BREACH": {
        "section": "Section 8(6)",
        "title": "Data Breach Notification",
        "description": (
            "Data Fiduciary must notify the Data Protection Board and each affected "
            "Data Principal in the event of a personal data breach, as prescribed."
        ),
    },
    "DATA_RETENTION": {
        "section": "Section 8(7)-(8)",
        "title": "Storage Limitation and Erasure",
        "description": (
            "Data Fiduciary must erase personal data when the purpose is no longer served "
            "or consent is withdrawn, unless retention is required by law. Inactivity "
            "periods and minimum log retention apply as prescribed."
        ),
    },
    "CONTACT_PUBLICATION": {
        "section": "Section 8(9)",
        "title": "Contact Information Publication",
        "description": (
            "Data Fiduciary must publish business contact information of the DPO (if applicable) "
            "or a designated person who can answer questions about processing."
        ),
    },
    "CHILD_DATA": {
        "section": "Section 9",
        "title": "Processing of Personal Data of Children",
        "description": (
            "Verifiable consent of parent or lawful guardian required. Tracking, behavioural "
            "monitoring and targeted advertising directed at children is prohibited."
        ),
    },
    "DISABILITY_GUARDIAN": {
        "section": "Section 9(1)",
        "title": "Processing of Data of Person with Disability",
        "description": (
            "Verifiable consent of lawful guardian required before processing personal data "
            "of a person with disability who has a lawful guardian."
        ),
    },
    "SIGNIFICANT_DATA_FIDUCIARY": {
        "section": "Section 10",
        "title": "Additional Obligations of Significant Data Fiduciary",
        "description": (
            "Significant Data Fiduciaries must appoint an India-based DPO, conduct periodic "
            "audits and DPIAs, and implement prescribed additional measures."
        ),
    },
    "DATA_PRINCIPAL_RIGHTS": {
        "section": "Section 11-14",
        "title": "Rights of Data Principal",
        "description": (
            "Data Principals have the right to access, correct, erase personal data, "
            "nominate representatives, and obtain information about shared processors."
        ),
    },
    "GRIEVANCE_REDRESSAL": {
        "section": "Section 8(10) & 13",
        "title": "Grievance Redressal",
        "description": (
            "Data Fiduciary must establish an effective grievance mechanism. Data Principals "
            "have the right to readily available means of grievance redressal with prescribed timelines."
        ),
    },
    "CROSS_BORDER_TRANSFER": {
        "section": "Section 16",
        "title": "Transfer of Personal Data Outside India",
        "description": (
            "Personal data may be transferred outside India except to countries "
            "restricted by the Central Government, subject to prescribed requirements."
        ),
    },
}

ALL_SECTIONS = list(DPDP_SECTIONS.keys())

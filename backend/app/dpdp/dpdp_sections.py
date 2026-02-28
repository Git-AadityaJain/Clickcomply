"""
DPDP Act (Digital Personal Data Protection Act, 2023) — Section Definitions.

This module defines the key sections of the DPDP Act that the compliance
engine evaluates. Each section maps to a specific regulatory obligation.

When the AI engine is integrated, these constants will be used to:
    - Tag identified compliance gaps to specific Act sections.
    - Generate section-specific recommendations.
    - Provide traceability from analysis results back to legislation.
"""

# Mapping of compliance area -> DPDP Act section reference
DPDP_SECTIONS = {
    "CONSENT": {
        "section": "Section 6",
        "title": "Consent of Data Principal",
        "description": (
            "Requires that personal data may only be processed for a lawful purpose "
            "after obtaining the consent of the Data Principal."
        ),
    },
    "NOTICE": {
        "section": "Section 5",
        "title": "Notice",
        "description": (
            "Every Data Fiduciary must give notice to the Data Principal "
            "before or at the time of seeking consent."
        ),
    },
    "PROCESSOR_DUTIES": {
        "section": "Section 8",
        "title": "General Obligations of Data Fiduciary",
        "description": (
            "Data Fiduciary must ensure completeness, accuracy, and consistency "
            "of personal data, and implement safeguards."
        ),
    },
    "DATA_PRINCIPAL_RIGHTS": {
        "section": "Section 11-14",
        "title": "Rights of Data Principal",
        "description": (
            "Data Principals have the right to access, correct, erase personal data, "
            "and nominate representatives."
        ),
    },
    "CHILD_DATA": {
        "section": "Section 9",
        "title": "Processing of Personal Data of Children",
        "description": (
            "Verifiable consent of the parent or lawful guardian is required "
            "before processing children's data. Profiling and tracking of "
            "children is prohibited."
        ),
    },
    "DATA_BREACH": {
        "section": "Section 8(6)",
        "title": "Data Breach Notification",
        "description": (
            "Data Fiduciary must notify the Data Protection Board and the "
            "affected Data Principal in the event of a personal data breach."
        ),
    },
    "CROSS_BORDER_TRANSFER": {
        "section": "Section 16",
        "title": "Transfer of Personal Data Outside India",
        "description": (
            "Personal data may be transferred outside India except to "
            "countries restricted by the Central Government."
        ),
    },
    "SIGNIFICANT_DATA_FIDUCIARY": {
        "section": "Section 10",
        "title": "Additional Obligations of Significant Data Fiduciary",
        "description": (
            "Significant Data Fiduciaries must appoint a DPO, conduct audits, "
            "and perform Data Protection Impact Assessments."
        ),
    },
}

# List of all section keys for iteration
ALL_SECTIONS = list(DPDP_SECTIONS.keys())

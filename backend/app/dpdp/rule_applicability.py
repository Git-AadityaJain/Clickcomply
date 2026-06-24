"""
Map organization profile to DPDP rule applicability — plain language for non-technical users.
"""

from __future__ import annotations

from app.dpdp.dpdp_rules import COMPLIANCE_RULES
from app.schemas.org_profile import (
    ApplicabilityReport,
    ApplicabilityStatus,
    AudienceType,
    DataCollected,
    DataStorageLocation,
    DpdpProcessingType,
    OrgProfile,
    RuleApplicability,
)

RULE_PLAIN_LABELS: dict[str, str] = {
    "RULE_NOTICE_001": "Privacy notice — what data you collect and why",
    "RULE_BOARD_001": "How to complain to the Data Protection Board",
    "RULE_CONSENT_001": "Getting and managing user consent",
    "RULE_CONSENT_MGR_001": "Consent Manager (if you use one)",
    "RULE_LEGITIMATE_001": "Processing without consent (legal exceptions)",
    "RULE_SECURITY_001": "Keeping personal data secure",
    "RULE_RETENTION_001": "How long you keep data and deletion",
    "RULE_RIGHTS_001": "User rights (access, correction, erasure)",
    "RULE_GRIEVANCE_001": "Grievance officer and complaints handling",
    "RULE_CONTACT_001": "Contact person for privacy questions",
    "RULE_CHILD_001": "Children's data (under 18)",
    "RULE_DISABILITY_001": "Data of persons with disability / guardians",
    "RULE_TRANSFER_001": "Storing or sending data outside India",
    "RULE_VENDOR_001": "Third parties who process data for you",
    "RULE_SDF_001": "Significant Data Fiduciary obligations",
    "RULE_BREACH_001": "Data breach notification",
}


def _uses_ai(profile: OrgProfile) -> bool:
    return profile.uses_ai == "yes"


def _uses_analytics(profile: OrgProfile) -> bool:
    return profile.uses_analytics_cookies == "yes"


def _has_foreign_hosting(profile: OrgProfile) -> bool:
    if profile.users_outside_india == "yes":
        return True
    return profile.data_storage_location != DataStorageLocation.INDIA


def _uses_third_parties(profile: OrgProfile) -> bool:
    return profile.uses_third_parties == "yes"


def evaluate_rule_applicability(profile: OrgProfile) -> ApplicabilityReport:
    rules: list[RuleApplicability] = []
    for rule in COMPLIANCE_RULES:
        rule_id = rule["rule_id"]
        status, reason = _evaluate_single(profile, rule_id)
        rules.append(
            RuleApplicability(
                rule_id=rule_id,
                section_ref=rule["section_ref"],
                plain_label=RULE_PLAIN_LABELS.get(rule_id, rule["description"]),
                status=status,
                reason=reason,
            )
        )
    applicable = [r for r in rules if r.status != ApplicabilityStatus.NOT_APPLICABLE]
    return ApplicabilityReport(
        rules=rules,
        applicable_count=len(applicable),
        skipped_count=len(rules) - len(applicable),
    )


def get_applicable_rules(profile: OrgProfile) -> list[dict]:
    report = evaluate_rule_applicability(profile)
    applicable_ids = {
        r.rule_id for r in report.rules if r.status != ApplicabilityStatus.NOT_APPLICABLE
    }
    return [r for r in COMPLIANCE_RULES if r["rule_id"] in applicable_ids]


def _evaluate_single(profile: OrgProfile, rule_id: str) -> tuple[ApplicabilityStatus, str]:
    if profile.sells_personal_data or profile.shares_for_advertising:
        if rule_id in ("RULE_NOTICE_001", "RULE_CONSENT_001"):
            return (
                ApplicabilityStatus.REQUIRED,
                "You indicated data is sold or shared — your notice and consent must say this clearly.",
            )

    if rule_id == "RULE_CHILD_001":
        if profile.platform_for_under_18 == "no":
            return ApplicabilityStatus.NOT_APPLICABLE, "You said your service is not for users under 18."
        return ApplicabilityStatus.REQUIRED, "You serve users under 18 — extra rules apply."

    if rule_id == "RULE_DISABILITY_001":
        if profile.platform_for_under_18 == "no" and profile.audience_type != AudienceType.EMPLOYEES:
            return ApplicabilityStatus.APPLICABLE, "Only needed if you process data of persons with disability with a guardian."
        return ApplicabilityStatus.REQUIRED, "May apply to your users — include if relevant."

    if rule_id == "RULE_CONSENT_MGR_001":
        if not _uses_ai(profile):
            return ApplicabilityStatus.NOT_APPLICABLE, "You do not use AI — a Consent Manager is usually not required."
        return ApplicabilityStatus.APPLICABLE, "If you use AI, explain how users control consent."

    if rule_id == "RULE_TRANSFER_001":
        if not _has_foreign_hosting(profile):
            return ApplicabilityStatus.APPLICABLE, "Confirm data stays in India or name any cross-border transfers."
        return ApplicabilityStatus.REQUIRED, "Data is stored outside India or you serve international users."

    if rule_id == "RULE_VENDOR_001":
        if not _uses_third_parties(profile):
            return ApplicabilityStatus.APPLICABLE, "Name any companies that process data on your behalf."
        return ApplicabilityStatus.REQUIRED, "You use third parties — contracts and disclosures are required."

    if rule_id == "RULE_SDF_001":
        return ApplicabilityStatus.APPLICABLE, "Large platforms may have extra duties — state if this applies to you."

    if rule_id == "RULE_BOARD_001":
        return ApplicabilityStatus.REQUIRED, "Every organization must tell users how to complain to the Board."

    if rule_id == "RULE_NOTICE_001":
        hint = "Your policy must list what personal data you collect and why."
        if _uses_analytics(profile):
            hint += " Include cookies and analytics."
        return ApplicabilityStatus.REQUIRED, hint

    if rule_id == "RULE_CONSENT_001":
        if profile.shares_for_advertising:
            return ApplicabilityStatus.REQUIRED, "Advertising or sharing data requires clear consent."
        return ApplicabilityStatus.REQUIRED, "Explain how users agree to data use."

    if rule_id == "RULE_LEGITIMATE_001":
        if profile.processing_type == DpdpProcessingType.EMPLOYEE_DATA:
            return ApplicabilityStatus.REQUIRED, "Employee data often relies on lawful exceptions — explain these."
        return ApplicabilityStatus.APPLICABLE, "Say when you process data without consent under the law."

    if rule_id == "RULE_SECURITY_001":
        return ApplicabilityStatus.REQUIRED, "Describe how you protect personal data."

    if rule_id == "RULE_RETENTION_001":
        return ApplicabilityStatus.REQUIRED, f"Say how long you keep data (you chose {profile.retention_period.value})."

    if rule_id == "RULE_RIGHTS_001":
        return ApplicabilityStatus.REQUIRED, "Explain how users can access, fix, or delete their data."

    if rule_id == "RULE_GRIEVANCE_001":
        return ApplicabilityStatus.REQUIRED, "Name your grievance officer and 90-day response process."

    if rule_id == "RULE_CONTACT_001":
        return ApplicabilityStatus.REQUIRED, "Publish a contact for privacy questions."

    if rule_id == "RULE_BREACH_001":
        return ApplicabilityStatus.REQUIRED, "Explain what you do if data is leaked or stolen."

    return ApplicabilityStatus.APPLICABLE, "Standard DPDP requirement for your type of processing."


def format_org_context(profile: OrgProfile) -> str:
    processing_labels = {
        DpdpProcessingType.DIGITAL_SERVICE: "Digital service collecting personal data",
        DpdpProcessingType.EMPLOYEE_DATA: "Employee/workforce data",
        DpdpProcessingType.VENDOR_PROCESSING: "Processing on behalf of clients",
        DpdpProcessingType.MINIMAL_CONTACT: "Minimal contact-form processing",
    }
    audience_labels = {
        AudienceType.PUBLIC: "General public",
        AudienceType.BUSINESS: "Business customers",
        AudienceType.EMPLOYEES: "Own employees only",
    }
    data_labels = {
        DataCollected.CONTACT: "Contact details (name, email, phone)",
        DataCollected.ACCOUNT: "Account and login data",
        DataCollected.UPLOADS: "User-uploaded files",
        DataCollected.TECHNICAL: "Technical logs (IP, device)",
    }
    location_labels = {
        DataStorageLocation.INDIA: "India",
        DataStorageLocation.US: "United States",
        DataStorageLocation.EU_UK: "EU / UK",
        DataStorageLocation.ASIA: "Asia (e.g. Singapore, UAE)",
        DataStorageLocation.MULTIPLE: "Multiple countries",
    }
    international = "Yes" if profile.users_outside_india == "yes" else "No"
    lines = [
        f"Legal name: {profile.legal_name}",
        f"Website: {profile.website_domain}",
        f"Contact: {profile.contact_email}",
        f"Grievance officer: {profile.grievance_officer_name}",
        f"Processing type: {processing_labels[profile.processing_type]}",
        f"Main audience: {audience_labels[profile.audience_type]}",
        f"Main data collected: {data_labels[profile.data_collected]}",
        f"Uses AI: {profile.uses_ai}",
        f"Data stored in: {location_labels[profile.data_storage_location]}",
        f"Third parties process data: {profile.uses_third_parties}",
        f"Analytics/cookies: {profile.uses_analytics_cookies}",
        f"Retention after account closed: {profile.retention_period.value}",
        f"Under-18 users: {profile.platform_for_under_18}",
        f"International customers/users: {international}",
        f"Security safeguards in place: {profile.has_security_safeguards}",
        f"Sells personal data: {profile.sells_personal_data}",
        f"Shares for advertising: {profile.shares_for_advertising}",
    ]
    return "\n".join(lines)

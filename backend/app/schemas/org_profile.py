"""
Organization processing profile — DPDP-focused questionnaire (simple, single-choice fields).
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class DpdpProcessingType(str, Enum):
    """Main processing activity under the DPDP Act."""
    DIGITAL_SERVICE = "digital_service"
    EMPLOYEE_DATA = "employee_data"
    VENDOR_PROCESSING = "vendor_processing"
    MINIMAL_CONTACT = "minimal_contact"


class AudienceType(str, Enum):
    PUBLIC = "public_users"
    BUSINESS = "business_clients"
    EMPLOYEES = "employees_only"


class DataCollected(str, Enum):
    CONTACT = "contact_info"
    ACCOUNT = "account_data"
    UPLOADS = "files_uploaded"
    TECHNICAL = "technical_logs"


class DataStorageLocation(str, Enum):
    INDIA = "india"
    US = "us"
    EU_UK = "eu_uk"
    ASIA = "asia"
    MULTIPLE = "multiple"


class RetentionChoice(str, Enum):
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    YEAR_1 = "1y"


class OrgProfile(BaseModel):
    """Per-document organization processing questionnaire."""

    legal_name: str = Field(..., min_length=1, max_length=255)
    website_domain: str = Field(..., min_length=1, max_length=255)
    contact_email: str = Field(..., min_length=3, max_length=255)
    grievance_officer_name: str = Field(..., min_length=1, max_length=255)
    grievance_officer_designation: str = Field(
        default="Grievance Officer",
        max_length=255,
    )

    processing_type: DpdpProcessingType
    audience_type: AudienceType
    data_collected: DataCollected

    uses_ai: Literal["yes", "no"] = "no"
    data_storage_location: DataStorageLocation = DataStorageLocation.INDIA
    uses_third_parties: Literal["yes", "no"] = "no"
    uses_analytics_cookies: Literal["yes", "no"] = "no"
    retention_period: RetentionChoice = RetentionChoice.DAYS_90

    platform_for_under_18: Literal["yes", "no"] = "no"
    users_outside_india: Literal["yes", "no"] = "no"
    has_security_safeguards: Literal["yes", "no"] = "yes"

    sells_personal_data: bool = False
    shares_for_advertising: bool = False


class ApplicabilityStatus(str, Enum):
    REQUIRED = "REQUIRED"
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RuleApplicability(BaseModel):
    rule_id: str
    section_ref: str
    plain_label: str
    status: ApplicabilityStatus
    reason: str


class ApplicabilityReport(BaseModel):
    rules: list[RuleApplicability]
    applicable_count: int
    skipped_count: int

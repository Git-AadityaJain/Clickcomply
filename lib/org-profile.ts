/**
 * DPDP-focused questionnaire — simple language, single-choice fields only.
 */

export type DpdpProcessingType =
  | "digital_service"
  | "employee_data"
  | "vendor_processing"
  | "minimal_contact"

export type AudienceType = "public_users" | "business_clients" | "employees_only"

export type DataCollected =
  | "contact_info"
  | "account_data"
  | "files_uploaded"
  | "technical_logs"

export type DataStorageLocation = "india" | "us" | "eu_uk" | "asia" | "multiple"

export type RetentionChoice = "30d" | "90d" | "1y"

export interface OrgProfile {
  legal_name: string
  website_domain: string
  contact_email: string
  grievance_officer_name: string
  grievance_officer_designation: string
  processing_type: DpdpProcessingType
  audience_type: AudienceType
  data_collected: DataCollected
  uses_ai: "yes" | "no"
  data_storage_location: DataStorageLocation
  uses_third_parties: "yes" | "no"
  uses_analytics_cookies: "yes" | "no"
  retention_period: RetentionChoice
  platform_for_under_18: "yes" | "no"
  users_outside_india: "yes" | "no"
  has_security_safeguards: "yes" | "no"
  sells_personal_data: boolean
  shares_for_advertising: boolean
}

export type ApplicabilityStatus = "REQUIRED" | "APPLICABLE" | "NOT_APPLICABLE"

export interface RuleApplicability {
  rule_id: string
  section_ref: string
  plain_label: string
  status: ApplicabilityStatus
  reason: string
}

export interface ApplicabilityReport {
  rules: RuleApplicability[]
  applicable_count: number
  skipped_count: number
}

export const FORM_COVERAGE_NOTE = "Choose the closest option."

export const PROCESSING_TYPE_OPTIONS: { value: DpdpProcessingType; label: string; hint: string }[] = [
  {
    value: "digital_service",
    label: "Website or app with user accounts",
    hint: "Notice, consent, and user rights (Sections 5–6)",
  },
  {
    value: "employee_data",
    label: "Mainly employee or HR records",
    hint: "Lawful uses for employment (Section 7)",
  },
  {
    value: "vendor_processing",
    label: "We process data for client companies",
    hint: "Data processor duties (Section 8)",
  },
  {
    value: "minimal_contact",
    label: "Simple contact form only",
    hint: "Basic notice obligations (Section 5)",
  },
]

export const AUDIENCE_OPTIONS: { value: AudienceType; label: string }[] = [
  { value: "public_users", label: "General public" },
  { value: "business_clients", label: "Business customers" },
  { value: "employees_only", label: "Our own staff" },
]

export const DATA_COLLECTED_OPTIONS: { value: DataCollected; label: string }[] = [
  { value: "contact_info", label: "Names, emails, phone numbers" },
  { value: "account_data", label: "Login and account details" },
  { value: "files_uploaded", label: "Files people upload" },
  { value: "technical_logs", label: "IP addresses and device info" },
]

export const STORAGE_OPTIONS: { value: DataStorageLocation; label: string }[] = [
  { value: "india", label: "India" },
  { value: "us", label: "United States" },
  { value: "eu_uk", label: "EU / UK" },
  { value: "asia", label: "Asia" },
  { value: "multiple", label: "Several countries" },
]

export const RETENTION_OPTIONS: { value: RetentionChoice; label: string }[] = [
  { value: "30d", label: "30 days" },
  { value: "90d", label: "90 days" },
  { value: "1y", label: "1 year" },
]

export const YES_NO_OPTIONS = [
  { value: "no" as const, label: "No" },
  { value: "yes" as const, label: "Yes" },
]

export function defaultOrgProfile(): OrgProfile {
  return {
    legal_name: "",
    website_domain: "",
    contact_email: "",
    grievance_officer_name: "",
    grievance_officer_designation: "Grievance Officer",
    processing_type: "digital_service",
    audience_type: "business_clients",
    data_collected: "contact_info",
    uses_ai: "no",
    data_storage_location: "india",
    uses_third_parties: "no",
    uses_analytics_cookies: "no",
    retention_period: "90d",
    platform_for_under_18: "no",
    users_outside_india: "no",
    has_security_safeguards: "yes",
    sells_personal_data: false,
    shares_for_advertising: false,
  }
}

export const WIZARD_STEPS = [
  { title: "Your company", description: "Basic details" },
  { title: "Your service", description: "What you do under DPDP" },
  { title: "Data & storage", description: "What you collect and where it lives" },
  { title: "Extra checks", description: "Children, international users, security" },
  { title: "Your policy", description: "Upload and optional suggested draft" },
] as const

export interface WizardCompletePayload {
  profile: OrgProfile
  policyFile: File | null
  generateDraft: boolean
  draftFormat: "docx" | "pdf"
}

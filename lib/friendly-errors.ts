/**
 * Turn API / validation errors into plain-language messages for non-technical users.
 */

type PydanticErrorItem = {
  loc?: (string | number)[]
  msg?: string
  type?: string
}

/** Wizard step name + what's wrong — keyed by API field name */
const FIELD_MESSAGES: Record<string, { step: string; label: string; fix: string }> = {
  legal_name: {
    step: "Step 1 — Your company",
    label: "Company name",
    fix: "Enter your company's legal name.",
  },
  website_domain: {
    step: "Step 1 — Your company",
    label: "Website",
    fix: "Enter your website address (e.g. https://example.com).",
  },
  contact_email: {
    step: "Step 1 — Your company",
    label: "Privacy email",
    fix: "Enter a valid contact email address.",
  },
  grievance_officer_name: {
    step: "Step 1 — Your company",
    label: "Grievance officer name",
    fix: "Enter the name of your grievance officer or privacy contact.",
  },
  grievance_officer_designation: {
    step: "Step 1 — Your company",
    label: "Grievance officer job title",
    fix: "Enter their job title.",
  },
  processing_type: {
    step: "Step 2 — Your service",
    label: "Main data processing",
    fix: "Choose the option that best describes your processing.",
  },
  audience_type: {
    step: "Step 2 — Your service",
    label: "Who uses your service",
    fix: "Choose who mainly uses your service.",
  },
  data_collected: {
    step: "Step 3 — Data & storage",
    label: "Personal data collected",
    fix: "Choose what personal data you collect most.",
  },
  data_storage_location: {
    step: "Step 3 — Data & storage",
    label: "Where data is stored",
    fix: "Choose where personal data is stored.",
  },
  uses_ai: {
    step: "Step 3 — Data & storage",
    label: "AI use",
    fix: "Answer whether you use AI on personal data.",
  },
  uses_third_parties: {
    step: "Step 3 — Data & storage",
    label: "Third-party processors",
    fix: "Answer whether outside companies help process data.",
  },
  uses_analytics_cookies: {
    step: "Step 3 — Data & storage",
    label: "Analytics / cookies",
    fix: "Answer whether you use analytics or non-essential cookies.",
  },
  retention_period: {
    step: "Step 3 — Data & storage",
    label: "Data retention",
    fix: "Choose how long you keep data after account deletion.",
  },
  platform_for_under_18: {
    step: "Step 4 — Extra checks",
    label: "Users under 18",
    fix: "Answer whether your service is meant for people under 18.",
  },
  users_outside_india: {
    step: "Step 4 — Extra checks",
    label: "International users",
    fix: "Answer whether you have customers or users outside India.",
  },
  has_security_safeguards: {
    step: "Step 4 — Extra checks",
    label: "Security measures",
    fix: "Answer whether you have basic security measures in place.",
  },
  sells_personal_data: {
    step: "Step 4 — Extra checks",
    label: "Selling personal data",
    fix: "Answer whether you sell personal data.",
  },
  shares_for_advertising: {
    step: "Step 4 — Extra checks",
    label: "Sharing data for advertising",
    fix: "Answer whether you share data for advertising.",
  },
}

function fieldFromLocation(loc: (string | number)[] | undefined): string | null {
  if (!loc?.length) return null
  const parts = loc.map(String)
  const idx = parts.indexOf("org_profile")
  const field = idx >= 0 ? parts[idx + 1] : parts[parts.length - 1]
  return field ?? null
}

function messageForField(field: string | null, rawMsg?: string): string {
  if (field && FIELD_MESSAGES[field]) {
    const { step, label, fix } = FIELD_MESSAGES[field]
    return `${step} → ${label}: ${fix}`
  }
  if (field) {
    const readable = field.replace(/_/g, " ")
    return `Questionnaire → ${readable}: ${rawMsg ?? "This answer is missing or invalid."}`
  }
  return rawMsg ?? "An answer is missing or invalid."
}

function hintFromPydanticItem(item: PydanticErrorItem): string {
  const field = fieldFromLocation(item.loc)
  const msg = item.msg ?? ""

  if (field === "contact_email" && (msg.toLowerCase().includes("email") || msg.includes("at least"))) {
    return messageForField("contact_email")
  }

  return messageForField(field, msg)
}

/** Return one line per missing/invalid field */
export function validationErrorLines(detail: unknown): string[] {
  if (typeof detail === "string") {
    return [detail]
  }

  if (Array.isArray(detail)) {
    const lines = detail.map((item) => hintFromPydanticItem(item as PydanticErrorItem))
    const unique = [...new Set(lines)]
    if (unique.length > 0) return unique
  }

  return ["We could not identify the problem. Go back through each step and check for empty fields."]
}

function humanizeValidationDetail(detail: unknown): string {
  if (typeof detail === "string") {
    const lower = detail.toLowerCase()
    if (lower.includes("not found")) {
      return "We could not find that review. It may have been removed — try starting a new questionnaire."
    }
    if (lower.includes("already in progress")) {
      return "A check is already running for this review. Please wait for it to finish."
    }
    if (lower.includes("no uploaded file") || lower.includes("no policy text")) {
      return "Upload your privacy policy (PDF or Word) before running a check."
    }
    return detail
  }

  const lines = validationErrorLines(detail)
  if (lines.length === 1) return lines[0]
  return lines.map((line) => `• ${line}`).join("\n")
}

export function friendlyApiError(
  status: number,
  detail: unknown,
  context?: "ingest" | "upload" | "analysis" | "general"
): string {
  if (status === 0 || detail === "Backend unreachable") {
    return "We cannot reach the server. Make sure the backend is running, then try again."
  }

  if (status === 422) {
    const human = humanizeValidationDetail(detail)
    if (context === "ingest" && !human.startsWith("•")) {
      return human
    }
    if (context === "ingest") {
      return `Please fix the following before we can save your answers:\n${human}`
    }
    return human
  }

  if (status === 404) {
    return humanizeValidationDetail(typeof detail === "string" ? detail : "not found")
  }

  if (status === 409) {
    return humanizeValidationDetail(detail)
  }

  if (status === 413) {
    return "That file is too large. Please upload a smaller PDF or Word document."
  }

  if (status >= 500) {
    return "Our server ran into a problem. Please wait a moment and try again."
  }

  return humanizeValidationDetail(detail)
}

export async function parseFriendlyError(
  res: Response,
  fallback: string,
  context?: "ingest" | "upload" | "analysis" | "general"
): Promise<string> {
  try {
    const body = await res.json()
    const detail = body?.detail ?? fallback
    return friendlyApiError(res.status, detail, context)
  } catch {
    return friendlyApiError(res.status, fallback, context)
  }
}

/**
 * API client for the ClickComply FastAPI backend.
 *
 * All frontend components call these functions instead of using fetch directly.
 * The base URL can be configured via NEXT_PUBLIC_API_URL environment variable.
 */

import type { OrgProfile, ApplicabilityReport } from "@/lib/org-profile"
import { parseFriendlyError, friendlyApiError } from "@/lib/friendly-errors"

export type { OrgProfile, ApplicabilityReport }

/** Backend URL for display (health messages, errors). */
const PUBLIC_API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000"

/** In dev, requests go through Next.js `/api` proxy (see next.config.mjs rewrites). */
export const API_BASE =
  process.env.NODE_ENV === "development" ? "/api" : PUBLIC_API_URL

/** Human-readable backend URL for offline / error messages */
export function formatBackendUrl(): string {
  try {
    const url = new URL(PUBLIC_API_URL)
    return url.host
  } catch {
    return PUBLIC_API_URL
  }
}

export interface HealthResponse {
  app?: string
  status?: string
  database?: string
  ai?: {
    status?: string
    ai_engine?: string
    message?: string
    model?: string
  }
}

async function parseErrorResponse(
  res: Response,
  fallback: string,
  context?: "ingest" | "upload" | "analysis" | "general"
): Promise<string> {
  return parseFriendlyError(res, fallback, context)
}

/** Types matching the FastAPI Pydantic schemas */

export interface DocumentIngestRequest {
  org_profile: OrgProfile
  document_name?: string | null
  document_type?: string
}

export interface DocumentIngestResponse {
  document_id: string
  status: string
  message: string
  generated_policy_available?: boolean
  applicability?: ApplicabilityReport | null
}

export interface DocumentStatusResponse {
  document_id: string
  status: string
}

export interface DocumentListItem {
  id: string
  document_name: string
  document_type: string
  status: string
  created_at: string
  file_size?: number
  upload_timestamp?: string
  uploader_ip?: string
  original_filename?: string
  stored_filename?: string
  remember?: boolean
  has_org_profile?: boolean
  has_generated_policy?: boolean
  has_uploaded_file?: boolean
}

export interface ComplianceGap {
  section: string
  description: string
  severity: string
}

export interface Recommendation {
  section: string
  action: string
  priority: string
}

export interface AnalysisProgress {
  current: number
  total: number
  rule_id: string
  rule_label: string
}

export interface PolicyComparison {
  summary: string
  missing_in_upload: string[]
  contradictions: string[]
  recommendations: string[]
}

export interface ComplianceAnalysisResponse {
  overall_status: string
  identified_gaps: ComplianceGap[]
  recommendations: Recommendation[]
  note: string
  progress?: AnalysisProgress | null
  rules_evaluated?: number | null
  skipped_rules?: string[] | null
  applicability_report?: ApplicabilityReport | null
  policy_comparison?: PolicyComparison | null
}

export interface AnalysisRerunResponse {
  document_id: string
  status: string
  message: string
}

/** POST /documents/ingest */
export async function ingestDocument(
  payload: DocumentIngestRequest
): Promise<DocumentIngestResponse> {
  const res = await fetch(`${API_BASE}/documents/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "ingest")
    throw new Error(detail)
  }
  return res.json()
}

/** GET /documents/{document_id}/status */
export async function getDocumentStatus(
  documentId: string
): Promise<DocumentStatusResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/status`)
  if (!res.ok) {
    throw new Error("We could not load the document status. Please refresh the page.")
  }
  return res.json()
}

/** GET /documents */
export async function listDocuments(): Promise<DocumentListItem[]> {
  const res = await fetch(`${API_BASE}/documents`)
  if (!res.ok) {
    throw new Error("We could not load your document list. Please refresh the page.")
  }
  return res.json()
}

/** GET /analysis/{document_id} */
export async function getAnalysis(
  documentId: string
): Promise<ComplianceAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analysis/${documentId}`)
  if (!res.ok) {
    throw new Error("We could not load the compliance results. Please try again.")
  }
  return res.json()
}

/** POST /analysis/{document_id}/rerun */
export async function rerunAnalysis(
  documentId: string
): Promise<AnalysisRerunResponse> {
  const res = await fetch(`${API_BASE}/analysis/${documentId}/rerun`, {
    method: "POST",
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "analysis")
    throw new Error(detail)
  }
  return res.json()
}

/** POST /documents/{document_id}/upload */
export async function uploadDocumentFile(
  documentId: string,
  file: File
): Promise<DocumentListItem> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/documents/${documentId}/upload`, {
    method: "POST",
    body: formData,
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "upload")
    throw new Error(detail)
  }
  return res.json()
}

async function fetchJson<T>(url: string): Promise<T> {
  let res: Response
  try {
    res = await fetch(url)
  } catch {
    throw new Error(friendlyApiError(0, "Backend unreachable"))
  }
  if (!res.ok) throw new Error(friendlyApiError(res.status, res.statusText))
  return res.json()
}

/** SWR fetcher helper */
export const fetcher = (url: string) => fetchJson(`${API_BASE}${url}`)

/** Health endpoint fetcher (shared across dashboard) */
export const healthFetcher = () => fetchJson<HealthResponse>(`${API_BASE}/health`)

export interface GeneratePolicyResponse {
  document_id: string
  format: string
  filename: string
  legal_name: string
}

export interface AnalysisCancelResponse {
  document_id: string
  status: string
  message: string
}

export interface ApplicabilityResponse {
  document_id: string
  report: ApplicabilityReport
}

/** POST /documents/{document_id}/generate-policy */
export async function generateSuggestedPolicy(
  documentId: string,
  format: "docx" | "pdf" = "docx"
): Promise<GeneratePolicyResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/generate-policy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ format }),
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "general")
    throw new Error(detail)
  }
  return res.json()
}

/** GET /documents/{document_id}/applicability */
export async function getApplicability(
  documentId: string
): Promise<ApplicabilityResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/applicability`)
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "general")
    throw new Error(detail)
  }
  return res.json()
}

/** POST /analysis/{document_id}/cancel */
export async function cancelAnalysis(documentId: string): Promise<AnalysisCancelResponse> {
  const res = await fetch(`${API_BASE}/analysis/${documentId}/cancel`, { method: "POST" })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "analysis")
    throw new Error(detail)
  }
  return res.json()
}

/** GET /analysis/{document_id}/download */
export async function downloadReviewReport(
  documentId: string,
  documentName: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/analysis/${documentId}/download`)
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "analysis")
    throw new Error(detail)
  }
  const blob = await res.blob()
  const safeName = documentName.replace(/[^\w\s-]/g, "").trim().slice(0, 80) || "review"
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `clickcomply-${safeName}.pdf`
  link.click()
  URL.revokeObjectURL(url)
}

/** POST /documents/prune-session */
export async function pruneSessionDocuments(
  keepDocumentIds: string[]
): Promise<{ removed_count: number; removed_ids: string[] }> {
  const res = await fetch(`${API_BASE}/documents/prune-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keep_document_ids: keepDocumentIds }),
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "general")
    throw new Error(detail)
  }
  return res.json()
}

/** PATCH /documents/{document_id}/remember */
export async function updateDocumentRemember(
  documentId: string,
  remember: boolean
): Promise<DocumentListItem> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/remember`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ remember }),
  })
  if (!res.ok) {
    const detail = await parseErrorResponse(res, res.statusText, "general")
    throw new Error(detail)
  }
  return res.json()
}

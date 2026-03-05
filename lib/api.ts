/**
 * API client for the ClickComply FastAPI backend.
 *
 * All frontend components call these functions instead of using fetch directly.
 * The base URL can be configured via NEXT_PUBLIC_API_URL environment variable.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

/** Types matching the FastAPI Pydantic schemas */

export interface DocumentIngestRequest {
  document_name: string
  document_type: string
}

export interface DocumentIngestResponse {
  document_id: string
  status: string
  message: string
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

export interface ComplianceAnalysisResponse {
  overall_status: string
  identified_gaps: ComplianceGap[]
  recommendations: Recommendation[]
  note: string
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
    throw new Error(`Ingest failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

/** GET /documents/{document_id}/status */
export async function getDocumentStatus(
  documentId: string
): Promise<DocumentStatusResponse> {
  const res = await fetch(`${API_BASE}/documents/${documentId}/status`)
  if (!res.ok) {
    throw new Error(`Status fetch failed: ${res.status}`)
  }
  return res.json()
}

/** GET /documents */
export async function listDocuments(): Promise<DocumentListItem[]> {
  const res = await fetch(`${API_BASE}/documents`)
  if (!res.ok) {
    throw new Error(`List documents failed: ${res.status}`)
  }
  return res.json()
}

/** GET /analysis/{document_id} */
export async function getAnalysis(
  documentId: string
): Promise<ComplianceAnalysisResponse> {
  const res = await fetch(`${API_BASE}/analysis/${documentId}`)
  if (!res.ok) {
    throw new Error(`Analysis fetch failed: ${res.status}`)
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
    throw new Error(`File upload failed: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

/** SWR fetcher helper */
export const fetcher = (url: string) =>
  fetch(`${API_BASE}${url}`).then((res) => {
    if (!res.ok) throw new Error(`Fetch failed: ${res.status}`)
    return res.json()
  })

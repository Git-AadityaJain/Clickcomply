"use client"

import useSWR from "swr"
import { FileText, FileCheck, FileLock2, FolderOpen, Loader2 } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { fetcher, type DocumentListItem } from "@/lib/api"
import { formatFileSize, formatUploadDate, formatUploadTime } from "@/lib/utils"

type DocStatus = "RECEIVED" | "QUEUED_FOR_ANALYSIS" | "AWAITING_AI_ANALYSIS"

const statusConfig: Record<string, { label: string; className: string }> = {
  RECEIVED: {
    label: "Received",
    className: "border-success/30 bg-success/10 text-success",
  },
  QUEUED_FOR_ANALYSIS: {
    label: "Queued",
    className: "border-warning/30 bg-warning/10 text-warning-foreground",
  },
  AWAITING_AI_ANALYSIS: {
    label: "Awaiting AI",
    className: "border-muted-foreground/30 bg-muted text-muted-foreground",
  },
}

function getTypeIcon(docType: string) {
  if (docType.includes("privacy")) {
    return <FileLock2 className="h-4 w-4 text-primary" />
  }
  if (docType.includes("dpa") || docType.includes("vendor")) {
    return <FileCheck className="h-4 w-4 text-chart-2" />
  }
  return <FileText className="h-4 w-4 text-chart-3" />
}

function formatType(docType: string): string {
  return docType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

/** Static fallback documents shown when backend is unreachable */
const fallbackDocuments: DocumentListItem[] = [
  {
    id: "demo-1",
    document_name: "Employee Data Protection Policy v2.4",
    document_type: "privacy_policy",
    status: "AWAITING_AI_ANALYSIS",
    created_at: "2026-02-28T10:00:00Z",
    file_size: 245632,
    upload_timestamp: "2026-02-28T10:15:00Z",
    uploader_ip: "203.0.113.42",
    original_filename: "privacy_policy_v2.4.pdf",
    stored_filename: "a7f2e9c1-privacy_policy_v2.4.pdf",
  },
  {
    id: "demo-2",
    document_name: "Vendor Data Processing Agreement - TechServ",
    document_type: "vendor_dpa",
    status: "QUEUED_FOR_ANALYSIS",
    created_at: "2026-02-27T10:00:00Z",
    file_size: 512000,
    upload_timestamp: "2026-02-27T14:30:00Z",
    uploader_ip: "203.0.113.43",
    original_filename: "TechServ_DPA.pdf",
    stored_filename: "b3d1f5e8-TechServ_DPA.pdf",
  },
  {
    id: "demo-3",
    document_name: "Internal Data Handling Guidelines",
    document_type: "internal_policy",
    status: "RECEIVED",
    created_at: "2026-02-26T10:00:00Z",
    file_size: 178245,
    upload_timestamp: "2026-02-26T09:45:00Z",
    uploader_ip: "203.0.113.44",
    original_filename: "data_handling_guidelines.docx",
    stored_filename: "c6e4a2f7-data_handling_guidelines.docx",
  },
  {
    id: "demo-4",
    document_name: "Customer Consent Management Policy",
    document_type: "privacy_policy",
    status: "AWAITING_AI_ANALYSIS",
    created_at: "2026-02-25T10:00:00Z",
    file_size: 342567,
    upload_timestamp: "2026-02-25T11:20:00Z",
    uploader_ip: "203.0.113.45",
    original_filename: "consent_policy.pdf",
    stored_filename: "d9f3b1c0-consent_policy.pdf",
  },
  {
    id: "demo-5",
    document_name: "Third-Party Data Sharing Agreement",
    document_type: "vendor_dpa",
    status: "QUEUED_FOR_ANALYSIS",
    created_at: "2026-02-24T10:00:00Z",
    file_size: 421890,
    upload_timestamp: "2026-02-24T16:00:00Z",
    uploader_ip: "203.0.113.46",
    original_filename: "3rd_party_sharing_agreement.pdf",
    stored_filename: "e2c5f8d3-3rd_party_sharing_agreement.pdf",
  },
]

export function DocumentsTable() {
  const { data, error, isLoading } = useSWR<DocumentListItem[]>(
    "/documents",
    fetcher,
    {
      fallbackData: fallbackDocuments,
      revalidateOnFocus: false,
      errorRetryCount: 2,
    }
  )

  const documents = data ?? fallbackDocuments
  const isUsingFallback = !!error

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <FolderOpen className="h-4 w-4 text-primary" />
          Uploaded Documents
          {isLoading && (
            <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
          )}
        </CardTitle>
        <CardDescription>
          {documents.length} document{documents.length !== 1 ? "s" : ""} uploaded for compliance review
          {isUsingFallback && (
            <span className="ml-1 text-muted-foreground/60">
              (showing demo data — backend offline)
            </span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Document Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Upload Date</TableHead>
              <TableHead>Upload Time</TableHead>
              <TableHead>File Size</TableHead>
              <TableHead>Uploaded By</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.map((doc) => {
              const status = statusConfig[doc.status] ?? {
                label: doc.status,
                className: "border-border bg-secondary text-muted-foreground",
              }
              return (
                <TableRow key={doc.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getTypeIcon(doc.document_type)}
                      <span className="font-medium text-foreground">
                        {doc.document_name}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {formatType(doc.document_type)}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatUploadDate(doc.upload_timestamp)}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground font-mono">
                    {formatUploadTime(doc.upload_timestamp)}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {doc.file_size ? formatFileSize(doc.file_size) : "—"}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground font-mono">
                    {doc.uploader_ip || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={status.className}>
                      {status.label}
                    </Badge>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

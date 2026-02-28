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
  },
  {
    id: "demo-2",
    document_name: "Vendor Data Processing Agreement - TechServ",
    document_type: "vendor_dpa",
    status: "QUEUED_FOR_ANALYSIS",
    created_at: "2026-02-27T10:00:00Z",
  },
  {
    id: "demo-3",
    document_name: "Internal Data Handling Guidelines",
    document_type: "internal_policy",
    status: "RECEIVED",
    created_at: "2026-02-26T10:00:00Z",
  },
  {
    id: "demo-4",
    document_name: "Customer Consent Management Policy",
    document_type: "privacy_policy",
    status: "AWAITING_AI_ANALYSIS",
    created_at: "2026-02-25T10:00:00Z",
  },
  {
    id: "demo-5",
    document_name: "Third-Party Data Sharing Agreement",
    document_type: "vendor_dpa",
    status: "QUEUED_FOR_ANALYSIS",
    created_at: "2026-02-24T10:00:00Z",
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
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Created</TableHead>
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
                  <TableCell>
                    <Badge variant="outline" className={status.className}>
                      {status.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-muted-foreground">
                    {new Date(doc.created_at).toLocaleDateString("en-IN")}
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

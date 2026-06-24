"use client"

import useSWR from "swr"
import { FileText, FileCheck, FileLock2, FolderOpen, Loader2, AlertCircle } from "lucide-react"
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
import { useDashboard } from "@/components/dashboard-provider"
import { useEffect } from "react"

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
  ANALYZING: {
    label: "Analyzing",
    className: "border-primary/30 bg-primary/10 text-primary",
  },
  ANALYSIS_COMPLETE: {
    label: "Complete",
    className: "border-success/30 bg-success/10 text-success",
  },
  ANALYSIS_FAILED: {
    label: "Failed",
    className: "border-destructive/30 bg-destructive/10 text-destructive",
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

export function DocumentsTable() {
  const { selectedDocumentId, setSelectedDocumentId } = useDashboard()
  const { data, error, isLoading } = useSWR<DocumentListItem[]>(
    "/documents",
    fetcher,
    {
      revalidateOnFocus: true,
      errorRetryCount: 2,
    }
  )

  const documents = data ?? []
  const backendOffline = !!error

  useEffect(() => {
    if (backendOffline || documents.length === 0) return
    const hasSelection = documents.some((d) => d.id === selectedDocumentId)
    if (!hasSelection) {
      setSelectedDocumentId(documents[0].id)
    }
  }, [documents, backendOffline, selectedDocumentId, setSelectedDocumentId])

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
          {backendOffline
            ? "Cannot reach backend — start the FastAPI server on port 8000"
            : `${documents.length} document${documents.length !== 1 ? "s" : ""} uploaded for compliance review`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {backendOffline ? (
          <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <p className="text-sm text-destructive">
              Backend offline. Run{" "}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">
                uvicorn app.main:app --reload
              </code>{" "}
              from the <code className="rounded bg-muted px-1 py-0.5 text-xs">backend/</code> folder.
            </p>
          </div>
        ) : documents.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No documents yet. Upload a PDF or DOCX above to start compliance review.
          </p>
        ) : (
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
                  <TableRow
                    key={doc.id}
                    className={`cursor-pointer ${
                      selectedDocumentId === doc.id ? "bg-primary/5" : ""
                    }`}
                    onClick={() => setSelectedDocumentId(doc.id)}
                  >
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
        )}
      </CardContent>
    </Card>
  )
}

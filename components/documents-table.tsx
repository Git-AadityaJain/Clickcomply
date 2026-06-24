"use client"

import { useEffect, useState, type MouseEvent } from "react"
import {
  FileText,
  FileCheck,
  FileLock2,
  FolderOpen,
  Loader2,
  Pin,
  Download,
} from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { downloadReviewReport, formatBackendUrl } from "@/lib/api"
import { formatFileSize, formatUploadDate, formatUploadTime } from "@/lib/utils"
import { useDashboard } from "@/components/dashboard-provider"
import { useDocuments } from "@/lib/hooks/use-documents"

const statusConfig: Record<string, { label: string; className: string }> = {
  RECEIVED: {
    label: "Received",
    className: "border-success/30 bg-success/10 text-success",
  },
  AWAITING_UPLOAD: {
    label: "Awaiting upload",
    className: "border-muted-foreground/30 bg-muted text-muted-foreground",
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
    return <FileLock2 className="h-4 w-4 shrink-0 text-primary" />
  }
  if (docType.includes("dpa") || docType.includes("vendor")) {
    return <FileCheck className="h-4 w-4 shrink-0 text-chart-2" />
  }
  return <FileText className="h-4 w-4 shrink-0 text-chart-3" />
}

function formatType(docType: string): string {
  return docType
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function DocumentsTable() {
  const { selectedDocumentId, setSelectedDocumentId, isBackendOnline } =
    useDashboard()
  const { documents, isLoading, isShowingOfflineRemembered, setRemember } =
    useDocuments()
  const [updatingId, setUpdatingId] = useState<string | null>(null)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const backendLabel = formatBackendUrl()
  const backendOffline = !isBackendOnline

  useEffect(() => {
    if (documents.length === 0) return
    const hasSelection = documents.some((d) => d.id === selectedDocumentId)
    if (!hasSelection) {
      setSelectedDocumentId(documents[0].id)
    }
  }, [documents, selectedDocumentId, setSelectedDocumentId])

  const description =
    backendOffline && isShowingOfflineRemembered
      ? `${documents.length} kept while offline`
      : documents.length > 0
        ? `${documents.length} review${documents.length !== 1 ? "s" : ""}`
        : null

  async function handleRememberChange(documentId: string, checked: boolean) {
    setUpdatingId(documentId)
    try {
      await setRemember(documentId, checked)
    } finally {
      setUpdatingId(null)
    }
  }

  function canDownloadReview(status: string) {
    return (
      status === "ANALYSIS_COMPLETE" ||
      status === "ANALYSIS_FAILED"
    )
  }

  async function handleDownloadReview(
    documentId: string,
    documentName: string,
    event: MouseEvent
  ) {
    event.stopPropagation()
    if (!isBackendOnline) return
    setDownloadingId(documentId)
    try {
      await downloadReviewReport(documentId, documentName)
    } catch {
      // User sees browser/network error; keep UI minimal
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <TooltipProvider>
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FolderOpen className="h-4 w-4 text-primary" />
            Documents
            {isLoading && (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
            )}
          </CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              {backendOffline
                ? `Server offline (${backendLabel}).`
                : "Nothing here yet. DPDP can't review thin air."}
            </p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/40 hover:bg-muted/40">
                    <TableHead className="w-12 text-center">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="inline-flex cursor-help items-center justify-center gap-1 text-xs font-medium">
                            <Pin className="h-3 w-3" />
                            Keep
                          </span>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-xs text-xs">
                          Checked files stay when you refresh or reopen the site,
                          and remain visible while the server is offline.
                        </TooltipContent>
                      </Tooltip>
                    </TableHead>
                    <TableHead>Document Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Upload Date</TableHead>
                    <TableHead>Upload Time</TableHead>
                    <TableHead>File Size</TableHead>
                    <TableHead>Uploaded By</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-12 text-center">PDF</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents.map((doc) => {
                    const status = statusConfig[doc.status] ?? {
                      label: doc.status,
                      className:
                        "border-border bg-secondary text-muted-foreground",
                    }
                    const isSelected = selectedDocumentId === doc.id
                    const isKept = doc.remember

                    return (
                      <TableRow
                        key={doc.id}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? "bg-primary/5" : ""
                        } ${isKept ? "border-l-2 border-l-primary/60" : ""}`}
                        onClick={() => setSelectedDocumentId(doc.id)}
                      >
                        <TableCell className="text-center">
                          <Checkbox
                            checked={isKept}
                            disabled={updatingId === doc.id}
                            aria-label={`Keep ${doc.document_name} after server restarts`}
                            onClick={(e) => e.stopPropagation()}
                            onCheckedChange={(value) =>
                              void handleRememberChange(
                                doc.id,
                                value === true
                              )
                            }
                            className="mx-auto data-[state=checked]:border-primary data-[state=checked]:bg-primary"
                          />
                        </TableCell>
                        <TableCell>
                          <div className="flex min-w-[10rem] items-center gap-2">
                            {getTypeIcon(doc.document_type)}
                            <span className="truncate font-medium text-foreground">
                              {doc.document_name}
                            </span>
                            {isKept && backendOffline && (
                              <Badge
                                variant="outline"
                                className="shrink-0 border-primary/30 bg-primary/5 text-[10px] text-primary"
                              >
                                Kept
                              </Badge>
                            )}
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
                        <TableCell className="font-mono text-sm text-muted-foreground">
                          {formatUploadTime(doc.upload_timestamp)}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {doc.file_size ? formatFileSize(doc.file_size) : "-"}
                        </TableCell>
                        <TableCell className="font-mono text-sm text-muted-foreground">
                          {doc.uploader_ip || "-"}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={status.className}>
                            {backendOffline && isKept ? "Kept (offline)" : status.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                type="button"
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                disabled={
                                  !isBackendOnline ||
                                  !canDownloadReview(doc.status) ||
                                  downloadingId === doc.id
                                }
                                aria-label={`Download PDF report for ${doc.document_name}`}
                                onClick={(e) =>
                                  void handleDownloadReview(
                                    doc.id,
                                    doc.document_name,
                                    e
                                  )
                                }
                              >
                                {downloadingId === doc.id ? (
                                  <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                  <Download className="h-4 w-4" />
                                )}
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="text-xs">
                              {!isBackendOnline
                                ? "Server offline"
                                : canDownloadReview(doc.status)
                                  ? "Download review PDF"
                                  : "Available when the check finishes"}
                            </TooltipContent>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </TooltipProvider>
  )
}

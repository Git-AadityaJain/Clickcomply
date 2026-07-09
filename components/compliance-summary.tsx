"use client"

import { useRef, useState } from "react"
import useSWR, { useSWRConfig } from "swr"
import {
  ClipboardList,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Lightbulb,
  Cpu,
  Loader2,
  RefreshCw,
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
import { Progress } from "@/components/ui/progress"
import { useDashboard } from "@/components/dashboard-provider"
import {
  getAnalysis,
  rerunAnalysis,
  cancelAnalysis,
  formatBackendUrl,
  AnalysisNotFoundError,
  type ComplianceAnalysisResponse,
} from "@/lib/api"

function shouldPollAnalysis(data?: ComplianceAnalysisResponse) {
  if (!data) return true
  return data.overall_status === "ANALYZING" || data.overall_status === "PENDING_AI_REVIEW"
}

function downloadBlob(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function exportAnalysisJson(
  documentId: string,
  analysis: ComplianceAnalysisResponse
) {
  downloadBlob(
    `clickcomply-analysis-${documentId.slice(0, 8)}.json`,
    JSON.stringify(analysis, null, 2),
    "application/json"
  )
}

function exportGapsCsv(
  documentId: string,
  analysis: ComplianceAnalysisResponse
) {
  const header = "section,severity,description"
  const rows = analysis.identified_gaps.map((gap) =>
    [gap.section, gap.severity, `"${gap.description.replace(/"/g, '""')}"`].join(",")
  )
  const recHeader = "\n\nsection,priority,action"
  const recRows = analysis.recommendations.map((rec) =>
    [rec.section, rec.priority, `"${rec.action.replace(/"/g, '""')}"`].join(",")
  )
  const csv = [header, ...rows, recHeader, ...recRows].join("\n")
  downloadBlob(
    `clickcomply-gaps-${documentId.slice(0, 8)}.csv`,
    csv,
    "text/csv"
  )
}

export function ComplianceSummary() {
  const { selectedDocumentId, isBackendOnline } = useDashboard()
  const { mutate } = useSWRConfig()
  const [rerunError, setRerunError] = useState<string | null>(null)
  const [cancelError, setCancelError] = useState<string | null>(null)
  const [isRerunning, setIsRerunning] = useState(false)
  const [isCancelling, setIsCancelling] = useState(false)

  const notFoundRef = useRef(false)

  const { data, error, isLoading } = useSWR(
    isBackendOnline && selectedDocumentId
      ? `/analysis/${selectedDocumentId}`
      : null,
    () => getAnalysis(selectedDocumentId!),
    {
      refreshInterval: (latest) =>
        isBackendOnline && !notFoundRef.current && shouldPollAnalysis(latest)
          ? 3000
          : 0,
      revalidateOnFocus: true,
      shouldRetryOnError: (err) => !(err instanceof AnalysisNotFoundError),
    }
  )

  const isAnalysisMissing = error instanceof AnalysisNotFoundError && !data
  notFoundRef.current = isAnalysisMissing

  async function handleCancel() {
    if (!selectedDocumentId) return
    setCancelError(null)
    setIsCancelling(true)
    try {
      await cancelAnalysis(selectedDocumentId)
      await mutate(`/analysis/${selectedDocumentId}`)
      await mutate("/documents")
    } catch (err) {
      setCancelError(err instanceof Error ? err.message : "Could not stop the check.")
    } finally {
      setIsCancelling(false)
    }
  }

  async function handleRerun() {
    if (!selectedDocumentId) return
    setRerunError(null)
    setIsRerunning(true)
    try {
      await rerunAnalysis(selectedDocumentId)
      await mutate(`/analysis/${selectedDocumentId}`)
      await mutate("/documents")
    } catch (err) {
      setRerunError(err instanceof Error ? err.message : "Re-run failed")
    } finally {
      setIsRerunning(false)
    }
  }

  if (!isBackendOnline) {
    const backendLabel = formatBackendUrl()
    const hasSelection = Boolean(selectedDocumentId)
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <ClipboardList className="h-4 w-4 text-primary" />
            Results
          </CardTitle>
          <CardDescription>Server offline</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {hasSelection
              ? `Reconnect to ${backendLabel} — your review is still on disk and will reload automatically.`
              : `Connect to ${backendLabel} to run checks.`}
          </p>
        </CardContent>
      </Card>
    )
  }

  if (!selectedDocumentId || isAnalysisMissing) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <ClipboardList className="h-4 w-4 text-primary" />
            Results
          </CardTitle>
          <CardDescription>DPDP check</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Fill out the form and run a check to see your compliance results here.
          </p>
        </CardContent>
      </Card>
    )
  }

  const analysis = data
  const isAnalyzing =
    analysis?.overall_status === "ANALYZING" ||
    analysis?.overall_status === "PENDING_AI_REVIEW"
  const canRerun =
    analysis &&
    !isAnalyzing &&
    !isRerunning &&
    analysis.overall_status !== "PENDING_AI_REVIEW"
  const canExport =
    analysis &&
    !isAnalyzing &&
    (analysis.identified_gaps.length > 0 ||
      analysis.recommendations.length > 0 ||
      analysis.overall_status === "COMPLIANT")

  const progressPercent = analysis?.progress
    ? Math.round((analysis.progress.current / analysis.progress.total) * 100)
    : isAnalyzing
      ? 8
      : 0

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <ClipboardList className="h-4 w-4 text-primary" />
              Results
              {(isLoading || isAnalyzing || isRerunning) && (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
              )}
            </CardTitle>
            <CardDescription>
              {analysis?.rules_evaluated && !isAnalyzing
                ? `${analysis.rules_evaluated} checks`
                : "DPDP check"}
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            {canExport && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => exportAnalysisJson(selectedDocumentId, analysis)}
                >
                  <Download className="mr-1.5 h-3.5 w-3.5" />
                  JSON
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => exportGapsCsv(selectedDocumentId, analysis)}
                >
                  <Download className="mr-1.5 h-3.5 w-3.5" />
                  CSV
                </Button>
              </>
            )}
            {isAnalyzing && (
              <Button variant="outline" size="sm" onClick={handleCancel} disabled={isCancelling}>
                Stop check
              </Button>
            )}
            {canRerun && (
              <Button variant="outline" size="sm" onClick={handleRerun} disabled={isRerunning}>
                <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                Check again
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        {error && !(error instanceof AnalysisNotFoundError) && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
            {error.message.includes("reach the server")
              ? error.message
              : `Could not load compliance results. ${error.message}`}
          </div>
        )}

        {rerunError && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
            {rerunError}
          </div>
        )}

        {cancelError && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
            {cancelError}
          </div>
        )}

        {isAnalyzing && (
          <div className="flex flex-col gap-2 rounded-lg border border-primary/20 bg-primary/5 p-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-foreground">Checking your policy…</span>
              {analysis?.progress ? (
                <span className="text-muted-foreground">
                  Step {analysis.progress.current} of {analysis.progress.total}
                </span>
              ) : (
                <span className="text-muted-foreground">Starting…</span>
              )}
            </div>
            <Progress value={progressPercent} className="h-2" />
            {analysis?.progress && (
              <p className="text-xs text-muted-foreground">{analysis.progress.rule_label}</p>
            )}
          </div>
        )}

        {analysis && (
          <>
            <div className="flex items-center justify-between gap-2">
              <StatusBadge status={analysis.overall_status} />
            </div>

            {analysis.note && (
              <div className="flex items-start gap-3 rounded-lg border border-border bg-secondary/50 p-4">
                <Cpu className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {analysis.note}
                </p>
              </div>
            )}

            <div className="flex flex-col gap-3">
              <h3 className="flex items-center gap-2 text-sm font-medium text-foreground">
                <AlertTriangle className="h-4 w-4 text-warning-foreground" />
                Issues found
                <span className="text-muted-foreground">
                  ({analysis.identified_gaps.length})
                </span>
              </h3>
              {analysis.identified_gaps.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {isAnalyzing
                    ? "Analysis in progress…"
                    : "No compliance gaps identified."}
                </p>
              ) : (
                <div className="flex flex-col gap-2">
                  {analysis.identified_gaps.map((gap, i) => (
                    <div
                      key={`${gap.section}-${i}`}
                      className="flex items-start justify-between gap-3 rounded-lg border border-border bg-card p-3"
                    >
                      <div className="flex flex-col gap-1">
                        <span className="text-xs font-mono text-muted-foreground">
                          {gap.section}
                        </span>
                        <span className="text-sm text-foreground">
                          {gap.description}
                        </span>
                      </div>
                      <SeverityBadge severity={gap.severity} />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-col gap-3">
              <h3 className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Lightbulb className="h-4 w-4 text-primary" />
                Suggested fixes
                <span className="text-muted-foreground">
                  ({analysis.recommendations.length})
                </span>
              </h3>
              {analysis.recommendations.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  {isAnalyzing
                    ? "Generating recommendations…"
                    : "No recommendations at this time."}
                </p>
              ) : (
                <div className="grid gap-2 sm:grid-cols-2">
                  {analysis.recommendations.map((rec, i) => (
                    <div
                      key={`${rec.section}-${i}`}
                      className="flex items-start gap-3 rounded-lg border border-border bg-card p-3"
                    >
                      <div className="mt-0.5 shrink-0">
                        {rec.priority === "CRITICAL" || rec.priority === "HIGH" ? (
                          <ShieldAlert className="h-4 w-4 text-destructive" />
                        ) : (
                          <ShieldCheck className="h-4 w-4 text-success" />
                        )}
                      </div>
                      <div>
                        <p className="text-xs font-mono text-muted-foreground">
                          {rec.section}
                        </p>
                        <p className="text-sm font-medium text-foreground">
                          {rec.action}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Priority: {rec.priority}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, string> = {
    COMPLIANT: "border-success/30 bg-success/10 text-success",
    NON_COMPLIANT: "border-destructive/30 bg-destructive/10 text-destructive",
    NEEDS_REVIEW: "border-warning/30 bg-warning/10 text-warning-foreground",
    ANALYZING: "border-primary/30 bg-primary/10 text-primary",
    PENDING_AI_REVIEW: "border-muted-foreground/30 bg-muted text-muted-foreground",
    ANALYSIS_CANCELLED: "border-muted-foreground/30 bg-muted text-muted-foreground",
    ANALYSIS_FAILED: "border-destructive/30 bg-destructive/10 text-destructive",
  }

  const labels: Record<string, string> = {
    COMPLIANT: "Looks good",
    NON_COMPLIANT: "Needs work",
    NEEDS_REVIEW: "Review suggested",
    ANALYZING: "Checking…",
    PENDING_AI_REVIEW: "Waiting",
    ANALYSIS_FAILED: "Check failed",
    ANALYSIS_CANCELLED: "Stopped",
  }

  return (
    <Badge variant="outline" className={config[status] ?? config.PENDING_AI_REVIEW}>
      {labels[status] ?? status.replace(/_/g, " ")}
    </Badge>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const normalized = severity.toUpperCase()
  const config: Record<string, string> = {
    CRITICAL: "border-destructive/30 bg-destructive/10 text-destructive",
    HIGH: "border-warning/30 bg-warning/10 text-warning-foreground",
    MEDIUM: "border-muted-foreground/20 bg-muted text-muted-foreground",
    LOW: "border-muted-foreground/20 bg-muted text-muted-foreground",
  }

  return (
    <Badge variant="outline" className={config[normalized] ?? config.MEDIUM}>
      {severity}
    </Badge>
  )
}

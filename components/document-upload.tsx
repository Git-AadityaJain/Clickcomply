"use client"

import { useEffect, useState } from "react"
import { Upload, CheckCircle2, AlertCircle, Download, X, WifiOff } from "lucide-react"
import { useSWRConfig } from "swr"
import {
  ingestDocument,
  uploadDocumentFile,
  generateSuggestedPolicy,
  formatBackendUrl,
  API_BASE,
} from "@/lib/api"
import type { ApplicabilityReport } from "@/lib/org-profile"
import type { WizardCompletePayload } from "@/lib/org-profile"
import { upsertCachedDocument } from "@/lib/document-cache"
import {
  clearActiveReview,
  loadActiveReview,
  saveActiveReview,
  type ActiveReviewState,
} from "@/lib/active-review-session"
import { useDashboard } from "@/components/dashboard-provider"
import { useHydrated } from "@/lib/hooks/use-hydrated"
import { OrgQuestionnaireWizard } from "@/components/org-questionnaire-wizard"
import { ApplicabilitySummary } from "@/components/applicability-summary"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

type FlowPhase = "questionnaire" | "done"
type UploadStage = "idle" | "saving" | "uploading" | "analyzing"

export function DocumentUpload() {
  const hydrated = useHydrated()
  const [phase, setPhase] = useState<FlowPhase>("questionnaire")
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [applicability, setApplicability] = useState<ApplicabilityReport | null>(null)
  const [draftReady, setDraftReady] = useState(false)
  const [draftFormat, setDraftFormat] = useState<"docx" | "pdf">("docx")
  const [stage, setStage] = useState<UploadStage>("idle")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { mutate } = useSWRConfig()
  const { setSelectedDocumentId, isBackendOnline } = useDashboard()
  const backendLabel = formatBackendUrl()

  useEffect(() => {
    const saved = loadActiveReview()
    if (!saved) return
    setPhase(saved.phase)
    setDocumentId(saved.documentId)
    setApplicability(saved.applicability)
    setDraftReady(saved.draftReady)
    setDraftFormat(saved.draftFormat)
    if (saved.documentId) {
      setSelectedDocumentId(saved.documentId)
    }
  }, [setSelectedDocumentId])

  function persistReviewState(next: ActiveReviewState) {
    saveActiveReview(next)
  }

  function resetAll() {
    clearActiveReview()
    setPhase("questionnaire")
    setDocumentId(null)
    setApplicability(null)
    setDraftReady(false)
    setStage("idle")
    setError(null)
  }

  async function handleComplete({ profile, policyFile, generateDraft, draftFormat: fmt }: WizardCompletePayload) {
    setError(null)
    setIsSubmitting(true)
    setStage("saving")
    try {
      const result = await ingestDocument({ org_profile: profile })
      const id = result.document_id
      setDocumentId(id)
      setApplicability(result.applicability ?? null)
      setSelectedDocumentId(id)

      if (generateDraft) {
        await generateSuggestedPolicy(id, fmt)
        setDraftReady(true)
        setDraftFormat(fmt)
      }

      if (policyFile) {
        setStage("uploading")
        await uploadDocumentFile(id, policyFile)
        setStage("analyzing")
        upsertCachedDocument({
          id,
          document_name: policyFile.name,
          document_type: "privacy_policy",
          status: "AWAITING_AI_ANALYSIS",
          created_at: new Date().toISOString(),
          file_size: policyFile.size,
          original_filename: policyFile.name,
          has_org_profile: true,
          has_generated_policy: generateDraft,
          has_uploaded_file: true,
          remember: false,
        })
      } else {
        upsertCachedDocument({
          id,
          document_name: `${profile.legal_name} — DPDP review`,
          document_type: "privacy_policy",
          status: "AWAITING_UPLOAD",
          created_at: new Date().toISOString(),
          has_org_profile: true,
          has_generated_policy: generateDraft,
          has_uploaded_file: false,
          remember: false,
        })
      }

      mutate("/documents")
      if (policyFile) mutate(`/analysis/${id}`)
      setPhase("done")
      setStage("idle")
      persistReviewState({
        phase: "done",
        documentId: id,
        applicability: result.applicability ?? null,
        draftReady: generateDraft,
        draftFormat: fmt,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.")
      setStage("idle")
    } finally {
      setIsSubmitting(false)
    }
  }

  function downloadDraft() {
    if (!documentId) return
    window.open(`${API_BASE}/documents/${documentId}/suggested-policy/download`, "_blank")
  }

  const savedReview = phase === "done" && documentId
  const showBackendOffline = hydrated && !isBackendOnline

  if (showBackendOffline && !savedReview) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Upload className="h-4 w-4 text-primary" />
            New privacy review
          </CardTitle>
          <CardDescription>
            Start the backend on {backendLabel}, then the frontend on localhost:3000.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (showBackendOffline && savedReview) {
    return (
      <div className="flex flex-col gap-4">
        <div className="flex items-start gap-2 rounded-lg border border-warning/30 bg-warning/5 p-3">
          <WifiOff className="mt-0.5 h-4 w-4 shrink-0 text-warning-foreground" />
          <p className="text-sm text-muted-foreground">
            Backend disconnected ({backendLabel}). Your review is saved — reconnect the server
            to continue checking results.
          </p>
        </div>
        {applicability && <ApplicabilitySummary report={applicability} />}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base text-success">
              <CheckCircle2 className="h-4 w-4" />
              Review saved
            </CardTitle>
            <CardDescription>
              Results and documents refresh automatically when the backend is back online.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  if (phase === "questionnaire") {
    return (
      <div className="flex flex-col gap-4">
        <OrgQuestionnaireWizard onComplete={handleComplete} disabled={isSubmitting} />
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <div className="text-sm text-destructive whitespace-pre-line">
              {error.split("\n").map((line, i) => (
                <p key={i} className={line.startsWith("•") ? "ml-1" : ""}>
                  {line}
                </p>
              ))}
            </div>
          </div>
        )}
        {stage !== "idle" && (
          <p className="text-center text-sm text-muted-foreground">
            {stage === "saving" && "Saving your answers…"}
            {stage === "uploading" && "Uploading your policy…"}
            {stage === "analyzing" && "Starting compliance check…"}
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {applicability && <ApplicabilitySummary report={applicability} />}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-success">
            <CheckCircle2 className="h-4 w-4" />
            Review saved
          </CardTitle>
          <CardDescription>
            {draftReady
              ? "Your suggested policy is ready to download. Uploaded policies are checked in the panel on the right."
              : "See the compliance summary when your uploaded policy finishes checking."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {draftReady && (
            <Button variant="secondary" onClick={downloadDraft}>
              <Download className="mr-2 h-4 w-4" />
              Download suggested policy ({draftFormat === "docx" ? "Word" : "PDF"})
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={resetAll}>
            <X className="mr-2 h-4 w-4" /> Start a new review
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

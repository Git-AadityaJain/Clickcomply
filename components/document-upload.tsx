"use client"

import { useState, useRef } from "react"
import { Upload, FileText, CheckCircle2, Clock, Cpu, X, AlertCircle } from "lucide-react"
import { useSWRConfig } from "swr"
import { ingestDocument } from "@/lib/api"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

type UploadStage =
  | "idle"
  | "sensed"
  | "queued"
  | "awaiting"

const stageConfig: Record<
  Exclude<UploadStage, "idle">,
  { label: string; icon: React.ReactNode; progress: number }
> = {
  sensed: {
    label: "Document sensed by backend",
    icon: <CheckCircle2 className="h-4 w-4 text-success" />,
    progress: 33,
  },
  queued: {
    label: "Queued for compliance analysis",
    icon: <Clock className="h-4 w-4 text-warning-foreground" />,
    progress: 66,
  },
  awaiting: {
    label: "Awaiting AI engine",
    icon: <Cpu className="h-4 w-4 text-muted-foreground" />,
    progress: 100,
  },
}

export function DocumentUpload() {
  const [stage, setStage] = useState<UploadStage>("idle")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { mutate } = useSWRConfig()

  function handleFileSelect(file: File) {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
    ]
    if (validTypes.includes(file.type) || file.name.endsWith(".pdf") || file.name.endsWith(".docx") || file.name.endsWith(".doc")) {
      setSelectedFile(file)
      setStage("idle")
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files?.[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files?.[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  async function handleSubmit() {
    if (!selectedFile) return

    setError(null)
    setStage("sensed")

    try {
      const docType = selectedFile.name.endsWith(".pdf")
        ? "privacy_policy"
        : "general_document"

      const result = await ingestDocument({
        document_name: selectedFile.name,
        document_type: docType,
      })

      setStage("queued")

      // Simulate the transition to awaiting (mirrors backend lifecycle)
      setTimeout(() => {
        setStage("awaiting")
        // Revalidate the documents list so the table updates
        mutate("/documents")
      }, 1500)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to submit document. Is the backend running?"
      )
      setStage("idle")
    }
  }

  function handleReset() {
    setSelectedFile(null)
    setStage("idle")
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const completedStages: Exclude<UploadStage, "idle">[] =
    stage === "sensed"
      ? ["sensed"]
      : stage === "queued"
        ? ["sensed", "queued"]
        : stage === "awaiting"
          ? ["sensed", "queued", "awaiting"]
          : []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Upload className="h-4 w-4 text-primary" />
          Document Upload
        </CardTitle>
        <CardDescription>
          Upload internal policies and documents for DPDP compliance review
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {/* Drop zone */}
        <div
          role="button"
          tabIndex={0}
          aria-label="Upload a PDF or DOCX file"
          className={`relative flex cursor-pointer flex-col items-center gap-3 rounded-lg border-2 border-dashed p-8 transition-colors ${
            isDragOver
              ? "border-primary bg-primary/5"
              : selectedFile
                ? "border-success/40 bg-success/5"
                : "border-border hover:border-primary/40 hover:bg-accent/50"
          }`}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragOver(true)
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              fileInputRef.current?.click()
            }
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            className="sr-only"
            onChange={handleInputChange}
          />
          {selectedFile ? (
            <>
              <FileText className="h-8 w-8 text-primary" />
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
                <Upload className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  Drop your file here or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports PDF and DOCX files
                </p>
              </div>
            </>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <Button
            onClick={handleSubmit}
            disabled={!selectedFile || stage !== "idle"}
            className="flex-1"
          >
            Submit for Compliance Review
          </Button>
          {selectedFile && (
            <Button variant="outline" size="icon" onClick={handleReset} aria-label="Remove file">
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Progress states */}
        {stage !== "idle" && (
          <div className="flex flex-col gap-3 rounded-lg border border-border bg-secondary/50 p-4">
            <Progress
              value={stageConfig[stage as Exclude<UploadStage, "idle">]?.progress ?? 0}
              className="h-1.5"
            />
            <div className="flex flex-col gap-2">
              {(["sensed", "queued", "awaiting"] as const).map((s) => {
                const isCompleted = completedStages.includes(s)
                const config = stageConfig[s]
                return (
                  <div
                    key={s}
                    className={`flex items-center gap-2 text-sm transition-opacity ${
                      isCompleted ? "opacity-100" : "opacity-30"
                    }`}
                  >
                    {config.icon}
                    <span className={isCompleted ? "text-foreground" : "text-muted-foreground"}>
                      {config.label}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

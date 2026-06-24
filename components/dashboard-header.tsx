"use client"

import { Shield, Activity, CircleHelp } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useBackendHealth } from "@/lib/hooks/use-backend-health"
import type { HealthResponse } from "@/lib/api"

function formatProviderLabel(engine?: string): string {
  if (!engine) return "unknown"
  return engine.charAt(0).toUpperCase() + engine.slice(1)
}

function formatAiStatusLabel(
  isOnline: boolean,
  isLoading: boolean,
  health?: HealthResponse
): { label: string; ready: boolean } {
  if (!isOnline) {
    return { label: "Backend offline", ready: false }
  }
  if (isLoading && !health) {
    return { label: "Connecting to backend…", ready: false }
  }

  const ai = health?.ai
  if (!ai) {
    return { label: "AI status unknown", ready: false }
  }

  const provider = formatProviderLabel(ai.ai_engine)
  const modelSuffix = ai.model ? ` · ${ai.model}` : ""

  if (ai.status === "READY") {
    return {
      label: `AI Engine Active (${provider}${modelSuffix})`,
      ready: true,
    }
  }
  if (ai.status === "NOT_CONFIGURED") {
    return {
      label: ai.message ?? `AI not configured (${provider})`,
      ready: false,
    }
  }
  if (ai.status === "ERROR") {
    return {
      label: ai.message ?? `AI engine error (${provider})`,
      ready: false,
    }
  }

  return {
    label: ai.message ?? `AI engine (${provider})`,
    ready: false,
  }
}

export function DashboardHeader() {
  const { health, isOnline, isLoading } = useBackendHealth()
  const { label: aiLabel, ready: aiReady } = formatAiStatusLabel(
    isOnline,
    isLoading,
    health
  )

  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto max-w-7xl px-6 py-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Shield className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-tight text-foreground">
                ClickComply
              </h1>
              <p className="text-sm text-muted-foreground">
                DPDP policy review
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5 text-muted-foreground"
              onClick={() =>
                document
                  .getElementById("help-faq")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              <CircleHelp className="h-4 w-4" />
              Help
            </Button>
            <Badge
              variant="outline"
              className={
                aiReady
                  ? "gap-1.5 border-success/30 bg-success/10 text-success"
                  : "gap-1.5 border-warning/30 bg-warning/10 text-warning-foreground"
              }
            >
              <Activity className="h-3 w-3" />
              {aiLabel}
            </Badge>
            <Badge variant="secondary" className="text-xs font-medium">
              India DPDP Framework
            </Badge>
          </div>
        </div>
      </div>
    </header>
  )
}

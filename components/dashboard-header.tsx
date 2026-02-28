import { Shield, Activity } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function DashboardHeader() {
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
                Compliance Dashboard
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge
              variant="outline"
              className="gap-1.5 border-warning/30 bg-warning/10 text-warning-foreground"
            >
              <Activity className="h-3 w-3" />
              Analysis Engine Pending
            </Badge>
            <Badge variant="secondary" className="font-mono text-xs">
              DPDP Act 2023
            </Badge>
          </div>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          AI-powered DPDP compliance — Upload policies and documents for automated compliance review
        </p>
      </div>
    </header>
  )
}

import { DashboardHeader } from "@/components/dashboard-header"
import { StatsBar } from "@/components/stats-bar"
import { DocumentUpload } from "@/components/document-upload"
import { DocumentsTable } from "@/components/documents-table"
import { ComplianceSummary } from "@/components/compliance-summary"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-col gap-8">
          {/* Stats overview */}
          <StatsBar />

          {/* Upload + Compliance side by side on desktop */}
          <div className="grid gap-8 lg:grid-cols-2">
            <DocumentUpload />
            <ComplianceSummary />
          </div>

          {/* Documents table full width */}
          <DocumentsTable />
        </div>
      </main>
      <footer className="border-t border-border bg-card">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <p className="text-xs text-muted-foreground">
            ClickComply — DPDP Act Compliance Platform
          </p>
          <p className="text-xs text-muted-foreground">
            Admin Dashboard v1.0
          </p>
        </div>
      </footer>
    </div>
  )
}

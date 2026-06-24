"use client"

import { DashboardHeader } from "@/components/dashboard-header"
import { StatsBar } from "@/components/stats-bar"
import { DocumentUpload } from "@/components/document-upload"
import { DocumentsTable } from "@/components/documents-table"
import { ComplianceSummary } from "@/components/compliance-summary"
import { DashboardProvider } from "@/components/dashboard-provider"
import { WelcomeDialog } from "@/components/welcome-dialog"
import { HelpFaqSection } from "@/components/help-faq-section"

export function DashboardShell() {
  return (
    <DashboardProvider>
      <div className="min-h-screen bg-background">
        <WelcomeDialog />
        <DashboardHeader />
        <main className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex flex-col gap-8">
            <StatsBar />
            <div className="grid gap-8 xl:grid-cols-2">
              <DocumentUpload />
              <ComplianceSummary />
            </div>
            <DocumentsTable />
            <HelpFaqSection />
          </div>
        </main>
      </div>
    </DashboardProvider>
  )
}

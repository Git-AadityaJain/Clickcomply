"use client"

import { Scale, CheckCircle2, MinusCircle } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { ApplicabilityReport } from "@/lib/org-profile"

interface ApplicabilitySummaryProps {
  report: ApplicabilityReport
}

export function ApplicabilitySummary({ report }: ApplicabilitySummaryProps) {
  const applies = report.rules.filter((r) => r.status !== "NOT_APPLICABLE")
  const skipped = report.rules.filter((r) => r.status === "NOT_APPLICABLE")

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Scale className="h-4 w-4 text-primary" />
          What we will check
        </CardTitle>
        <CardDescription>
          {applies.length} DPDP requirements apply to your answers
          {skipped.length > 0 ? ` · ${skipped.length} do not apply` : ""}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <Section title="Applies to you" icon={<CheckCircle2 className="h-4 w-4 text-success" />} items={applies} />
        {skipped.length > 0 && (
          <Section title="Does not apply" icon={<MinusCircle className="h-4 w-4 text-muted-foreground" />} items={skipped} muted />
        )}
      </CardContent>
    </Card>
  )
}

function Section({
  title,
  icon,
  items,
  muted,
}: {
  title: string
  icon: React.ReactNode
  items: ApplicabilityReport["rules"]
  muted?: boolean
}) {
  return (
    <div>
      <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
        {icon}
        {title}
      </h3>
      <ul className={`flex flex-col gap-2 text-sm ${muted ? "text-muted-foreground" : ""}`}>
        {items.map((rule) => (
          <li key={rule.rule_id} className="rounded-md border border-border px-3 py-2">
            <p className="font-medium">{rule.plain_label}</p>
            <p className="text-xs opacity-80">{rule.reason}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

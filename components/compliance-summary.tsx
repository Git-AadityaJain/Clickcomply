import {
  ClipboardList,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Lightbulb,
  Cpu,
} from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function ComplianceSummary() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <ClipboardList className="h-4 w-4 text-primary" />
          Compliance Review Summary
        </CardTitle>
        <CardDescription>
          DPDP Act gap analysis and compliance recommendations
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        {/* AI Status Notice */}
        <div className="flex items-start gap-3 rounded-lg border border-border bg-secondary/50 p-4">
          <Cpu className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
          <div className="flex flex-col gap-1">
            <p className="text-sm font-medium text-foreground">
              AI analysis not yet integrated
            </p>
            <p className="text-sm leading-relaxed text-muted-foreground">
              This section will display DPDP gaps, risks, and recommendations once the AI compliance engine is connected.
            </p>
          </div>
        </div>

        {/* Placeholder: Identified Gaps */}
        <div className="flex flex-col gap-3">
          <h3 className="flex items-center gap-2 text-sm font-medium text-foreground">
            <AlertTriangle className="h-4 w-4 text-warning-foreground" />
            Identified Gaps
          </h3>
          <div className="flex flex-col gap-2">
            {[
              {
                title: "Consent mechanism not documented",
                severity: "Critical" as const,
              },
              {
                title: "Data processing purpose unclear",
                severity: "High" as const,
              },
              {
                title: "Grievance officer details missing",
                severity: "Medium" as const,
              },
            ].map((gap) => (
              <div
                key={gap.title}
                className="flex items-center justify-between rounded-lg border border-dashed border-border bg-card p-3 opacity-50"
              >
                <span className="text-sm text-muted-foreground">
                  {gap.title}
                </span>
                <SeverityBadge severity={gap.severity} />
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-muted-foreground">
            Placeholder data — pending AI engine integration
          </p>
        </div>

        {/* Placeholder: Recommendations */}
        <div className="flex flex-col gap-3">
          <h3 className="flex items-center gap-2 text-sm font-medium text-foreground">
            <Lightbulb className="h-4 w-4 text-primary" />
            Recommendations
          </h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {[
              {
                title: "Update privacy notice",
                desc: "Align with Section 6 of DPDP Act",
                icon: <ShieldAlert className="h-4 w-4 text-destructive" />,
              },
              {
                title: "Implement consent logs",
                desc: "Track and store explicit consent records",
                icon: <ShieldCheck className="h-4 w-4 text-success" />,
              },
            ].map((rec) => (
              <div
                key={rec.title}
                className="flex items-start gap-3 rounded-lg border border-dashed border-border bg-card p-3 opacity-50"
              >
                <div className="mt-0.5 shrink-0">{rec.icon}</div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {rec.title}
                  </p>
                  <p className="text-xs text-muted-foreground/70">
                    {rec.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-muted-foreground">
            Placeholder data — pending AI engine integration
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

function SeverityBadge({ severity }: { severity: "Critical" | "High" | "Medium" }) {
  const config = {
    Critical: "border-destructive/30 bg-destructive/10 text-destructive",
    High: "border-warning/30 bg-warning/10 text-warning-foreground",
    Medium: "border-muted-foreground/20 bg-muted text-muted-foreground",
  }

  return (
    <Badge variant="outline" className={config[severity]}>
      {severity}
    </Badge>
  )
}

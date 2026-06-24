"use client"

import type React from "react"
import { FileText, CheckCircle2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { useDocuments } from "@/lib/hooks/use-documents"

export function StatsBar() {
  const { documents } = useDocuments()
  const total = documents.length
  const complete = documents.filter((d) => d.status === "ANALYSIS_COMPLETE").length

  const stats = [
    total > 0 && {
      label: "Reviews started",
      value: String(total),
      icon: <FileText className="h-4 w-4" />,
      accent: "text-primary",
      bg: "bg-primary/10",
    },
    complete > 0 && {
      label: "Checks complete",
      value: String(complete),
      icon: <CheckCircle2 className="h-4 w-4" />,
      accent: "text-success",
      bg: "bg-success/10",
    },
  ].filter(Boolean) as {
    label: string
    value: string
    icon: React.ReactNode
    accent: string
    bg: string
  }[]

  if (stats.length === 0) return null

  return (
    <div
      className={`grid gap-4 ${stats.length === 1 ? "grid-cols-1 max-w-xs" : "grid-cols-2"}`}
    >
      {stats.map((stat) => (
        <Card key={stat.label} className="py-4">
          <CardContent className="flex items-center gap-3 px-4">
            <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${stat.bg} ${stat.accent}`}>
              {stat.icon}
            </div>
            <div>
              <p className="text-2xl font-semibold tracking-tight text-foreground">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

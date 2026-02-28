"use client"

import useSWR from "swr"
import { FileText, Clock, Cpu, CheckCircle2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { fetcher, type DocumentListItem } from "@/lib/api"

export function StatsBar() {
  const { data } = useSWR<DocumentListItem[]>("/documents", fetcher, {
    revalidateOnFocus: false,
    errorRetryCount: 2,
  })

  const documents = data ?? []
  const total = documents.length
  const received = documents.filter((d) => d.status === "RECEIVED").length
  const queued = documents.filter((d) => d.status === "QUEUED_FOR_ANALYSIS").length
  const awaiting = documents.filter(
    (d) => d.status === "AWAITING_AI_ANALYSIS"
  ).length

  const stats = [
    {
      label: "Total Documents",
      value: String(total || "0"),
      icon: <FileText className="h-4 w-4" />,
      accent: "text-primary",
      bg: "bg-primary/10",
    },
    {
      label: "Received",
      value: String(received),
      icon: <CheckCircle2 className="h-4 w-4" />,
      accent: "text-success",
      bg: "bg-success/10",
    },
    {
      label: "Queued",
      value: String(queued),
      icon: <Clock className="h-4 w-4" />,
      accent: "text-warning-foreground",
      bg: "bg-warning/10",
    },
    {
      label: "Awaiting AI",
      value: String(awaiting),
      icon: <Cpu className="h-4 w-4" />,
      accent: "text-muted-foreground",
      bg: "bg-muted",
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="py-4">
          <CardContent className="flex items-center gap-3 px-4">
            <div
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${stat.bg} ${stat.accent}`}
            >
              {stat.icon}
            </div>
            <div>
              <p className="text-2xl font-semibold tracking-tight text-foreground">
                {stat.value}
              </p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

import { AuthGate } from "@/components/auth-gate"
import { DashboardShell } from "@/components/dashboard-shell"

export default function DashboardPage() {
  return (
    <AuthGate>
      <DashboardShell />
    </AuthGate>
  )
}

"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Shield } from "lucide-react"

import { canAccessApp } from "@/lib/auth"

/**
 * Client-side gate for the dashboard. Sends users to /login unless they are
 * signed in or have chosen "Skip for now". Avoids a flash of dashboard content
 * by rendering a brief loading state until the check completes.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [allowed, setAllowed] = useState(false)

  useEffect(() => {
    if (canAccessApp()) {
      setAllowed(true)
    } else {
      router.replace("/login")
    }
  }, [router])

  if (!allowed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <div className="flex h-10 w-10 animate-pulse items-center justify-center rounded-lg bg-primary">
            <Shield className="h-5 w-5 text-primary-foreground" />
          </div>
          <p className="text-sm">Loading ClickComply…</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

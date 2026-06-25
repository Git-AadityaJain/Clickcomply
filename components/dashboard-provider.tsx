"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react"
import { useSWRConfig } from "swr"
import { useBackendHealth } from "@/lib/hooks/use-backend-health"
import { runSessionCleanup } from "@/lib/document-session"

interface DashboardContextValue {
  selectedDocumentId: string | null
  setSelectedDocumentId: (id: string | null) => void
  isBackendOnline: boolean
  isBackendLoading: boolean
  isSessionReady: boolean
}

const DashboardContext = createContext<DashboardContextValue | null>(null)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    null
  )
  const [isSessionReady, setIsSessionReady] = useState(false)
  const selectedDocumentIdRef = useRef<string | null>(null)
  const sessionCleanupDone = useRef(false)
  const { isOnline, isLoading } = useBackendHealth()
  const { mutate } = useSWRConfig()

  selectedDocumentIdRef.current = selectedDocumentId

  useEffect(() => {
    if (isLoading) return

    if (!isOnline) {
      setIsSessionReady(true)
      return
    }

    // Prune ephemeral reviews once per page load — not on every health reconnect.
    if (sessionCleanupDone.current) {
      setIsSessionReady(true)
      return
    }
    sessionCleanupDone.current = true

    let cancelled = false
    setIsSessionReady(false)

    void (async () => {
      try {
        const removedIds = await runSessionCleanup()
        if (cancelled) return

        const selectedId = selectedDocumentIdRef.current
        if (selectedId && removedIds.includes(selectedId)) {
          setSelectedDocumentId(null)
        }

        await mutate("/documents")
      } catch {
        // Still allow the dashboard to load if prune fails
      } finally {
        if (!cancelled) {
          setIsSessionReady(true)
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [isOnline, isLoading, mutate])

  useEffect(() => {
    if (isOnline) return

    void mutate("/documents", undefined, { revalidate: false })
    void mutate(
      (key) => typeof key === "string" && key.startsWith("/analysis/"),
      undefined,
      { revalidate: false }
    )
  }, [isOnline, mutate])

  const value = useMemo(
    () => ({
      selectedDocumentId,
      setSelectedDocumentId,
      isBackendOnline: isOnline,
      isBackendLoading: isLoading,
      isSessionReady,
    }),
    [selectedDocumentId, isOnline, isLoading, isSessionReady]
  )

  return (
    <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>
  )
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) {
    throw new Error("useDashboard must be used within DashboardProvider")
  }
  return ctx
}

export function useSelectDocument() {
  const { setSelectedDocumentId } = useDashboard()
  return useCallback(
    (id: string | null) => setSelectedDocumentId(id),
    [setSelectedDocumentId]
  )
}

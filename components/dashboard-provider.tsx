"use client"

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react"

interface DashboardContextValue {
  selectedDocumentId: string | null
  setSelectedDocumentId: (id: string | null) => void
}

const DashboardContext = createContext<DashboardContextValue | null>(null)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    null
  )

  const value = useMemo(
    () => ({
      selectedDocumentId,
      setSelectedDocumentId,
    }),
    [selectedDocumentId]
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

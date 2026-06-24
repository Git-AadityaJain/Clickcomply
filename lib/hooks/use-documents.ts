"use client"

import { useCallback, useEffect, useMemo, useSyncExternalStore } from "react"
import useSWR from "swr"
import {
  applyRememberOverrides,
  clearPendingRemember,
  getDocumentCacheRevision,
  getOfflineRememberedDocuments,
  getPendingRememberSyncs,
  setDocumentRememberLocal,
  subscribeDocumentCache,
  syncDocumentsFromServer,
  type CachedDocument,
} from "@/lib/document-cache"
import {
  fetcher,
  updateDocumentRemember,
  type DocumentListItem,
} from "@/lib/api"
import { useDashboard } from "@/components/dashboard-provider"
import { useHydrated } from "@/lib/hooks/use-hydrated"

export function useDocuments() {
  const hydrated = useHydrated()
  const { isBackendOnline, isSessionReady } = useDashboard()
  const cacheRevision = useSyncExternalStore(
    subscribeDocumentCache,
    getDocumentCacheRevision,
    () => 0
  )

  const { data, isLoading, mutate } = useSWR<DocumentListItem[]>(
    isBackendOnline && isSessionReady ? "/documents" : null,
    fetcher,
    {
      revalidateOnFocus: true,
      refreshInterval: isBackendOnline ? 5000 : 0,
      errorRetryCount: 1,
    }
  )

  useEffect(() => {
    if (!data || !isBackendOnline) return
    syncDocumentsFromServer(data)

    const pending = getPendingRememberSyncs()
    const ids = Object.keys(pending)
    if (ids.length === 0) return

    void (async () => {
      for (const id of ids) {
        const serverDoc = data.find((d) => d.id === id)
        if (!serverDoc) {
          clearPendingRemember(id)
          continue
        }
        if ((serverDoc.remember ?? false) === pending[id]) {
          clearPendingRemember(id)
          continue
        }
        try {
          await updateDocumentRemember(id, pending[id])
          clearPendingRemember(id)
        } catch {
          // Keep pending; retry on next fetch cycle
        }
      }
      void mutate()
    })()
  }, [data, isBackendOnline, mutate])

  const documents: CachedDocument[] = useMemo(() => {
    void cacheRevision
    if (!hydrated) return []
    if (isBackendOnline) {
      return applyRememberOverrides(data ?? [])
    }
    return getOfflineRememberedDocuments()
  }, [hydrated, isBackendOnline, data, cacheRevision])

  const setRemember = useCallback(
    async (documentId: string, remember: boolean) => {
      setDocumentRememberLocal(documentId, remember)

      if (isBackendOnline) {
        try {
          await updateDocumentRemember(documentId, remember)
          clearPendingRemember(documentId)
          void mutate()
        } catch {
          // Pending flag remains for retry
        }
      }
    },
    [isBackendOnline, mutate]
  )

  return {
    documents,
    isLoading: isBackendOnline && (!isSessionReady || isLoading),
    isShowingOfflineRemembered: !isBackendOnline && documents.length > 0,
    setRemember,
    refresh: mutate,
  }
}

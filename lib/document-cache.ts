/**
 * Browser-side cache for document list + remember preferences.
 * Remembered documents stay visible across refresh; others are cleared on load.
 */

import { API_BASE, type DocumentListItem } from "@/lib/api"

export type CachedDocument = DocumentListItem & { remember: boolean }

interface DocumentCacheStore {
  documents: Record<string, CachedDocument>
  pendingRemember: Record<string, boolean>
}

const STORAGE_KEY = `clickcomply-document-cache:${API_BASE}`

let cacheRevision = 0
const cacheListeners = new Set<() => void>()

function bumpCacheRevision() {
  cacheRevision += 1
  cacheListeners.forEach((listener) => listener())
}

export function getDocumentCacheRevision(): number {
  return cacheRevision
}

export function subscribeDocumentCache(listener: () => void): () => void {
  cacheListeners.add(listener)
  return () => cacheListeners.delete(listener)
}

function emptyStore(): DocumentCacheStore {
  return { documents: {}, pendingRemember: {} }
}

function readStore(): DocumentCacheStore {
  if (typeof window === "undefined") return emptyStore()
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyStore()
    const parsed = JSON.parse(raw) as DocumentCacheStore
    if (!parsed?.documents || typeof parsed.documents !== "object") {
      return emptyStore()
    }
    return {
      documents: parsed.documents,
      pendingRemember: parsed.pendingRemember ?? {},
    }
  } catch {
    return emptyStore()
  }
}

function writeStore(store: DocumentCacheStore) {
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
  bumpCacheRevision()
}

export function syncDocumentsFromServer(docs: DocumentListItem[]) {
  const store = readStore()
  const nextDocs: Record<string, CachedDocument> = { ...store.documents }

  for (const doc of docs) {
    const remember =
      doc.id in store.pendingRemember
        ? store.pendingRemember[doc.id]
        : (doc.remember ?? false)
    nextDocs[doc.id] = { ...doc, remember }
  }

  writeStore({ ...store, documents: nextDocs })
}

export function getOfflineRememberedDocuments(): CachedDocument[] {
  const store = readStore()
  return Object.values(store.documents)
    .filter((doc) => {
      const pending = store.pendingRemember[doc.id]
      const remember = pending !== undefined ? pending : doc.remember
      return remember
    })
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
}

export function applyRememberOverrides(
  docs: DocumentListItem[]
): CachedDocument[] {
  const store = readStore()
  return docs.map((doc) => ({
    ...doc,
    remember:
      doc.id in store.pendingRemember
        ? store.pendingRemember[doc.id]
        : (doc.remember ?? false),
  }))
}

export function setDocumentRememberLocal(documentId: string, remember: boolean) {
  const store = readStore()
  const existing = store.documents[documentId]
  if (existing) {
    store.documents[documentId] = { ...existing, remember }
  }
  store.pendingRemember[documentId] = remember
  writeStore(store)
}

export function clearPendingRemember(documentId: string) {
  const store = readStore()
  delete store.pendingRemember[documentId]
  writeStore(store)
}

export function getPendingRememberSyncs(): Record<string, boolean> {
  return { ...readStore().pendingRemember }
}

/** Document IDs the user marked to keep in this browser. */
export function getLocallyKeptDocumentIds(): string[] {
  const store = readStore()
  const ids = new Set<string>()

  for (const doc of Object.values(store.documents)) {
    const pending = store.pendingRemember[doc.id]
    const remember = pending !== undefined ? pending : doc.remember
    if (remember) ids.add(doc.id)
  }

  for (const [id, remember] of Object.entries(store.pendingRemember)) {
    if (remember) ids.add(id)
  }

  return [...ids]
}

/** Drop non-kept reviews from browser storage after a session prune. */
export function pruneEphemeralFromCache() {
  const store = readStore()
  const nextDocs: Record<string, CachedDocument> = {}
  const nextPending: Record<string, boolean> = {}

  for (const [id, doc] of Object.entries(store.documents)) {
    const pending = store.pendingRemember[id]
    const remember = pending !== undefined ? pending : doc.remember
    if (!remember) continue
    nextDocs[id] = { ...doc, remember: true }
    if (pending !== undefined) {
      nextPending[id] = pending
    }
  }

  for (const [id, remember] of Object.entries(store.pendingRemember)) {
    if (remember && !(id in nextDocs)) {
      nextPending[id] = true
    }
  }

  writeStore({ documents: nextDocs, pendingRemember: nextPending })
}

export function upsertCachedDocument(doc: CachedDocument) {
  const store = readStore()
  store.documents[doc.id] = doc
  writeStore(store)
}

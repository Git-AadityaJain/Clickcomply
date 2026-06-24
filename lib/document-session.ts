/**
 * Browser session startup: sync keep flags, prune ephemeral reviews on the server,
 * and trim local cache so only kept documents survive a refresh.
 */

import {
  clearPendingRemember,
  getLocallyKeptDocumentIds,
  getPendingRememberSyncs,
  pruneEphemeralFromCache,
} from "@/lib/document-cache"
import {
  listDocuments,
  pruneSessionDocuments,
  updateDocumentRemember,
} from "@/lib/api"

async function syncPendingRememberFlags(): Promise<void> {
  const pending = getPendingRememberSyncs()
  const ids = Object.keys(pending)
  if (ids.length === 0) return

  let serverDocs
  try {
    serverDocs = await listDocuments()
  } catch {
    return
  }

  for (const id of ids) {
    const serverDoc = serverDocs.find((d) => d.id === id)
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
      // Keep pending; keep_document_ids still protects remember=true on prune
    }
  }
}

export async function runSessionCleanup(): Promise<string[]> {
  await syncPendingRememberFlags()
  const keepIds = getLocallyKeptDocumentIds()
  const { removed_ids } = await pruneSessionDocuments(keepIds)
  pruneEphemeralFromCache()
  return removed_ids
}

/**
 * Persists in-progress / completed review flow state for the current browser tab.
 * Survives brief backend disconnects without resetting the questionnaire panel.
 */

import type { ApplicabilityReport } from "@/lib/org-profile"

export interface ActiveReviewState {
  phase: "questionnaire" | "done"
  documentId: string | null
  applicability: ApplicabilityReport | null
  draftReady: boolean
  draftFormat: "docx" | "pdf"
}

const STORAGE_KEY = "clickcomply-active-review"

export function loadActiveReview(): ActiveReviewState | null {
  if (typeof window === "undefined") return null
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as ActiveReviewState
  } catch {
    return null
  }
}

export function saveActiveReview(state: ActiveReviewState): void {
  if (typeof window === "undefined") return
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

export function clearActiveReview(): void {
  if (typeof window === "undefined") return
  sessionStorage.removeItem(STORAGE_KEY)
}

"use client"

import { useSyncExternalStore } from "react"

function subscribe() {
  return () => {}
}

function getSnapshot() {
  return true
}

function getServerSnapshot() {
  return false
}

/** True only after the client has hydrated (false during SSR and the first client pass). */
export function useHydrated() {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}

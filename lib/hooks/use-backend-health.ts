"use client"

import useSWR from "swr"
import { healthFetcher, type HealthResponse } from "@/lib/api"
import { useHydrated } from "@/lib/hooks/use-hydrated"

const HEALTH_POLL_MS = 5000

export function useBackendHealth() {
  const hydrated = useHydrated()
  const { data, error, isLoading, isValidating } = useSWR<HealthResponse>(
    "/health",
    healthFetcher,
    {
      revalidateOnFocus: true,
      refreshInterval: HEALTH_POLL_MS,
      errorRetryCount: 1,
      dedupingInterval: 2000,
    }
  )

  const isOnline = hydrated && !error && !!data

  return {
    health: isOnline ? data : undefined,
    isOnline,
    isLoading: !hydrated || (isLoading && !data && !error),
    isValidating,
    error,
  }
}

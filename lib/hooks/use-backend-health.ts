"use client"

import useSWR from "swr"
import {
  healthFetcher,
  livenessFetcher,
  type HealthResponse,
  type LivenessResponse,
} from "@/lib/api"
import { useHydrated } from "@/lib/hooks/use-hydrated"

const LIVENESS_POLL_MS = 5000
const HEALTH_POLL_MS = 30000

export function useBackendHealth() {
  const hydrated = useHydrated()

  const {
    data: live,
    error: liveError,
    isLoading: liveLoading,
    isValidating: liveValidating,
  } = useSWR<LivenessResponse>(
    hydrated ? "/health/live" : null,
    livenessFetcher,
    {
      revalidateOnFocus: true,
      refreshInterval: LIVENESS_POLL_MS,
      errorRetryCount: 3,
      dedupingInterval: 2000,
      shouldRetryOnError: true,
    }
  )

  const { data: health, isLoading: healthLoading } = useSWR<HealthResponse>(
    hydrated && live ? "/health" : null,
    healthFetcher,
    {
      revalidateOnFocus: true,
      refreshInterval: HEALTH_POLL_MS,
      errorRetryCount: 2,
      dedupingInterval: 5000,
    }
  )

  // Keep showing online while a previous liveness response is cached (SWR retains
  // data on transient revalidation failures so brief hiccups don't flip the UI).
  const isOnline =
    hydrated &&
    Boolean(live) &&
    !(liveError && !live && !liveLoading && !liveValidating)

  const isLoading = !hydrated || (liveLoading && !live)

  return {
    health: isOnline ? health : undefined,
    isOnline,
    isLoading,
    isValidating: liveValidating,
    error: liveError,
    isHealthLoading: healthLoading,
  }
}

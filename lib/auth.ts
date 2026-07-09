/**
 * Client-side auth state for ClickComply.
 *
 * Phase 2 (foundation): tokens are stored in localStorage and a "skip" flag
 * lets users bypass the login page while the backend still runs with
 * REQUIRE_AUTH=false. When auth is enforced later, the same token store and
 * gate logic apply — only the skip path goes away.
 */

const ACCESS_TOKEN_KEY = "cc_access_token"
const REFRESH_TOKEN_KEY = "cc_refresh_token"
const SKIP_KEY = "cc_auth_skipped"

export interface AuthTokens {
  access_token: string
  refresh_token: string
}

function isBrowser(): boolean {
  return typeof window !== "undefined"
}

export function getAccessToken(): string | null {
  if (!isBrowser()) return null
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  if (!isBrowser()) return null
  return window.localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function saveTokens(tokens: AuthTokens): void {
  if (!isBrowser()) return
  window.localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token)
  window.localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token)
  // A real session supersedes a prior "skip".
  window.localStorage.removeItem(SKIP_KEY)
}

export function clearAuth(): void {
  if (!isBrowser()) return
  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  window.localStorage.removeItem(REFRESH_TOKEN_KEY)
  window.localStorage.removeItem(SKIP_KEY)
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null
}

/** Whether the user chose to skip login for now. */
export function hasSkippedAuth(): boolean {
  if (!isBrowser()) return false
  return window.localStorage.getItem(SKIP_KEY) === "true"
}

export function setSkippedAuth(): void {
  if (!isBrowser()) return
  window.localStorage.setItem(SKIP_KEY, "true")
}

/** User may proceed to the dashboard if signed in OR has skipped. */
export function canAccessApp(): boolean {
  return isAuthenticated() || hasSkippedAuth()
}

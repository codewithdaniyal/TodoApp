/**
 * Token storage utilities for JWT management
 * Handles both localStorage and cookie storage for client-side token storage
 * Cookie is needed for middleware (server-side) authentication checks
 */

'use client'

export const TOKEN_KEY = 'auth-token'

/**
 * Set a cookie with the given name and value
 */
function setCookie(name: string, value: string, days: number = 1): void {
  if (typeof document === 'undefined') return
  const expires = new Date(Date.now() + days * 864e5).toUTCString()
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`
}

/**
 * Get a cookie value by name
 */
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift()
    return cookieValue ? decodeURIComponent(cookieValue) : null
  }
  return null
}

/**
 * Delete a cookie by name
 */
function deleteCookie(name: string): void {
  if (typeof document === 'undefined') return
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`
}

/**
 * Store authentication token in both localStorage and cookie
 * @param token JWT token from Better Auth
 */
export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return
  // Store in localStorage for API client
  localStorage.setItem(TOKEN_KEY, token)
  // Store in cookie for middleware (server-side) auth checks
  setCookie(TOKEN_KEY, token, 1) // 1 day expiry
}

/**
 * Retrieve authentication token from localStorage
 * @returns JWT token or null if not found
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Clear authentication token from both localStorage and cookie
 * Call this on signout or when token becomes invalid
 */
export function clearAuthToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
  deleteCookie(TOKEN_KEY)
}

/**
 * Check if user is authenticated (has valid token)
 * Note: This only checks presence, not validity
 * Backend will validate the token signature
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}

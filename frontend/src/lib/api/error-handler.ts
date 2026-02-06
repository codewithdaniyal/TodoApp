/**
 * Error Handler (T029)
 * Centralized error handling with 401 authentication error handling
 */

'use client'

import { clearAuthToken } from '../auth/session'

export interface APIError {
  error: string
  message: string
  detail?: string
}

/**
 * Handle API errors with special handling for 401 Unauthorized
 * @param error Error object from API
 * @returns Formatted error message
 */
export function handleAPIError(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  if (typeof error === 'object' && error !== null && 'message' in error) {
    return (error as APIError).message
  }

  return 'An unexpected error occurred'
}

/**
 * Handle 401 Unauthorized errors
 * Clears authentication token and redirects to signin
 */
export function handle401Error(): void {
  clearAuthToken()

  if (typeof window !== 'undefined') {
    window.location.href = '/signin?error=session_expired'
  }
}

/**
 * Check if error is authentication related
 * @param error Error to check
 * @returns True if error is 401 or authentication related
 */
export function isAuthError(error: unknown): boolean {
  if (typeof error === 'object' && error !== null) {
    const apiError = error as Partial<APIError>
    return (
      apiError.error === 'AuthenticationError' ||
      apiError.error === 'TokenExpired' ||
      (apiError.message?.includes('Authentication required') ?? false)
    )
  }
  return false
}

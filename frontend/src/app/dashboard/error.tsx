/**
 * Dashboard Error Boundary
 * Handles errors in dashboard with recovery option
 */

'use client'

import { useEffect } from 'react'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to error reporting service
    console.error('Dashboard error:', error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center space-y-6">
        <div className="flex justify-center">
          <div className="rounded-full bg-red-100 p-3">
            <svg
              className="h-12 w-12 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-gray-900">Something went wrong</h2>
          <p className="text-gray-600">
            We encountered an error while loading your dashboard. Please try again.
          </p>
        </div>

        <button
          onClick={reset}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  )
}

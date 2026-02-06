/**
 * Global Error Boundary Component
 * Catches unhandled errors and displays user-friendly message
 */

'use client'

import { Component, ReactNode } from 'react'
import { clearAuthToken } from '@/lib/auth/session'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  isAuthError: boolean
  errorMessage: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      isAuthError: false,
      errorMessage: '',
    }
  }

  static getDerivedStateFromError(error: Error): State {
    const isAuthError = error.message.includes('Authentication required') ||
                        error.message.includes('401')

    return {
      hasError: true,
      isAuthError,
      errorMessage: error.message,
    }
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error)

    // Handle authentication errors
    if (this.state.isAuthError) {
      clearAuthToken()
      if (typeof window !== 'undefined') {
        window.location.href = '/signin?error=session_expired'
      }
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.state.isAuthError) {
        return null // Redirecting to signin
      }

      return this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <h2 className="text-2xl font-bold text-red-600 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-700 mb-4">
              {this.state.errorMessage || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

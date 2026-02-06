/**
 * useAuth Hook (T022)
 * React hook for authentication state and operations
 */

'use client'

import { useState, useEffect } from 'react'
import { signin, signup, signout, isAuthenticated, type User, type SigninData, type SignupData } from '@/lib/auth/better-auth'

interface UseAuthReturn {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  signin: (data: SigninData) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  signout: () => void
  error: string | null
}

/**
 * Hook for managing authentication state
 * Provides signin, signup, signout, and session state
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = isAuthenticated()
      setIsLoading(false)

      // Note: We don't fetch user data here because backend doesn't have /me endpoint
      // User data will be set during signin/signup
    }

    checkAuth()
  }, [])

  const handleSignin = async (data: SigninData) => {
    try {
      setError(null)
      setIsLoading(true)
      const response = await signin(data)
      setUser(response.data.user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignup = async (data: SignupData) => {
    try {
      setError(null)
      setIsLoading(true)
      const response = await signup(data)
      setUser(response.data.user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignout = () => {
    setUser(null)
    signout()
  }

  return {
    user,
    isLoading,
    isAuthenticated: isAuthenticated(),
    signin: handleSignin,
    signup: handleSignup,
    signout: handleSignout,
    error,
  }
}

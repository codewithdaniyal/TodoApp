/**
 * Better Auth Configuration (T020)
 * Integrates with FastAPI JWT backend for authentication
 */

'use client'

import { apiClient } from '../api/client'
import { setAuthToken, clearAuthToken } from './session'

export interface User {
  id: number
  email: string
  created_at?: string
}

export interface AuthResponse {
  data: {
    user: User
    token: string
    expires_at?: string
  }
  message: string
}

export interface SignupData {
  email: string
  password: string
  name?: string
}

export interface SigninData {
  email: string
  password: string
}

/**
 * Sign up new user account
 * @param data User registration data
 * @returns User object and JWT token
 */
export async function signup(data: SignupData): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/auth/signup', data)

  // Store JWT token in localStorage and cookie
  if (response.data?.token) {
    setAuthToken(response.data.token)
  }

  return response
}

/**
 * Sign in existing user
 * @param data User credentials
 * @returns User object and JWT token
 */
export async function signin(data: SigninData): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/auth/signin', data)

  // Store JWT token in localStorage and cookie
  if (response.data?.token) {
    setAuthToken(response.data.token)
  }

  return response
}

/**
 * Sign out current user
 * Clears authentication token from localStorage
 */
export function signout(): void {
  clearAuthToken()

  // Redirect to signin page
  if (typeof window !== 'undefined') {
    window.location.href = '/signin'
  }
}

/**
 * Verify authentication status
 * Checks if JWT token exists in localStorage
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  return localStorage.getItem('auth-token') !== null
}

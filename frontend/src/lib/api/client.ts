/**
 * API Client for Todo Backend
 * Automatically injects JWT tokens and handles 401 errors
 */

'use client'

export interface APIResponse<T> {
  data: T
  message?: string
}

export interface APIError {
  error: string
  message: string
  detail?: string
}

class APIClient {
  private baseURL: string

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }

  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Get JWT token from localStorage
    const token = typeof window !== 'undefined'
      ? localStorage.getItem('auth-token')
      : null

    // Build headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    // Attach Bearer token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        ...options,
        headers,
      })

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        // Clear token and redirect to signin
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-token')
          window.location.href = '/signin?error=session_expired'
        }
        throw new Error('Authentication required')
      }

      // Handle other error responses
      if (!response.ok) {
        const error: APIError = await response.json().catch(() => ({
          error: 'RequestError',
          message: `HTTP ${response.status}`,
        }))
        throw new Error(error.message || `HTTP ${response.status}`)
      }

      // Parse and return JSON response
      const data = await response.json()
      return data as T
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // HTTP method helpers
  async get<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'GET' })
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async put<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(url: string): Promise<T> {
    return this.request<T>(url, { method: 'DELETE' })
  }
}

// Export singleton instance
export const apiClient = new APIClient()

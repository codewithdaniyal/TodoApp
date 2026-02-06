/**
 * Next.js Middleware (T026)
 * Protects /dashboard routes and redirects unauthenticated users to signin
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Get auth token from cookies or check if it exists in localStorage (will be set client-side)
  const token = request.cookies.get('auth-token')?.value
  const { pathname } = request.nextUrl

  // Protected routes - require authentication
  const protectedRoutes = ['/dashboard']
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route))

  // If accessing protected route without token, redirect to signin
  if (isProtectedRoute && !token) {
    const url = request.nextUrl.clone()
    url.pathname = '/signin'
    url.searchParams.set('redirect', pathname)
    return NextResponse.redirect(url)
  }

  // If accessing auth pages (signin/signup) with valid token, redirect to dashboard
  const authRoutes = ['/signin', '/signup']
  const isAuthRoute = authRoutes.includes(pathname)

  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}

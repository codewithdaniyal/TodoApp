/**
 * Auth API Route Handler
 * Proxies authentication requests to FastAPI backend
 * This route is not needed since we're using direct API calls to FastAPI
 * Keeping it as a placeholder to satisfy Next.js routing structure
 */

import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  return NextResponse.json(
    { error: 'Authentication is handled directly through FastAPI backend' },
    { status: 404 }
  )
}

export async function POST(request: NextRequest) {
  return NextResponse.json(
    { error: 'Authentication is handled directly through FastAPI backend' },
    { status: 404 }
  )
}

/**
 * Root Layout (T028)
 * Global layout with Tailwind CSS and metadata
 */

import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A modern full-stack todo application with user authentication',
  keywords: ['todo', 'task management', 'productivity'],
  authors: [{ name: 'Todo App Team' }],
  openGraph: {
    title: 'Todo App - Manage Your Tasks',
    description: 'A modern full-stack todo application with user authentication',
    type: 'website',
    url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Todo App - Manage Your Tasks',
    description: 'A modern full-stack todo application with user authentication',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  )
}

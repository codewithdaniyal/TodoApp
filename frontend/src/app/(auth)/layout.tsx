/**
 * Auth Layout (T025)
 * Shared layout for signin and signup pages
 */

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
      <div className="max-w-md w-full">
        {children}
      </div>
    </div>
  )
}

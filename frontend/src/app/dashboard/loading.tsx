/**
 * Dashboard Loading State
 * Displays while dashboard content is loading
 */

export default function DashboardLoading() {
  return (
    <div className="space-y-8">
      {/* Header Skeleton */}
      <div className="space-y-2">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-4 w-64 bg-gray-200 rounded animate-pulse"></div>
      </div>

      {/* Form Skeleton */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="h-6 w-32 bg-gray-200 rounded animate-pulse mb-4"></div>
        <div className="flex gap-3">
          <div className="flex-1 h-10 bg-gray-200 rounded animate-pulse"></div>
          <div className="w-24 h-10 bg-gray-200 rounded animate-pulse"></div>
        </div>
      </div>

      {/* Task List Skeleton */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="h-6 w-40 bg-gray-200 rounded animate-pulse mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="h-5 w-5 bg-gray-200 rounded animate-pulse"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-1/4"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

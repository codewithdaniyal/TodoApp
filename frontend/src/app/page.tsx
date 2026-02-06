/**
 * Landing Page (T027)
 * Home page with links to signin/signup
 */

import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-4">
      <div className="max-w-4xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Side - Content */}
        <div className="text-center lg:text-left space-y-6">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
              TaskFlow
            </h1>
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Streamline Your Productivity
            </h2>
            <p className="text-lg text-gray-600 max-w-lg mx-auto lg:mx-0">
              Manage your tasks efficiently with our AI-powered todo application. 
              Stay organized, boost productivity, and achieve your goals faster.
            </p>
          </div>

          <div className="space-y-4 pt-6">
            <Link
              href="/signin"
              className="block w-full md:w-auto mx-auto lg:mx-0 bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-4 px-8 rounded-xl font-semibold hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="block w-full md:w-auto mx-auto lg:mx-0 bg-white text-indigo-600 py-4 px-8 rounded-xl font-semibold border-2 border-indigo-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all duration-300 shadow-sm hover:shadow-md"
            >
              Create Account
            </Link>
          </div>

          <div className="pt-6 text-sm text-gray-500">
            <p>Secure authentication • AI task assistant • Responsive design • Real-time sync</p>
          </div>
        </div>

        {/* Right Side - Visual Elements */}
        <div className="hidden lg:flex justify-center">
          <div className="relative">
            {/* Floating elements */}
            <div className="absolute -top-6 -left-6 w-32 h-32 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
            <div className="absolute top-10 -right-6 w-32 h-32 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-32 h-32 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
            
            {/* Main card */}
            <div className="relative bg-white rounded-2xl shadow-xl border border-gray-100 p-6 w-80">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Today's Tasks</h3>
                <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">3 done</span>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <div className="w-5 h-5 rounded-full border-2 border-green-500 flex items-center justify-center mr-3">
                    <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <span className="text-gray-700 line-through">Review quarterly report</span>
                </div>
                
                <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                  <div className="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center mr-3">
                    <svg className="w-3 h-3 text-transparent" fill="none" stroke="currentColor" viewBox="0 0 24 24"></svg>
                  </div>
                  <span className="text-gray-700">Prepare presentation</span>
                </div>
                
                <div className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <div className="w-5 h-5 rounded-full border-2 border-green-500 flex items-center justify-center mr-3">
                    <svg className="w-3 h-3 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <span className="text-gray-700 line-through">Team meeting</span>
                </div>
                
                <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                  <div className="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center mr-3">
                    <svg className="w-3 h-3 text-transparent" fill="none" stroke="currentColor" viewBox="0 0 24 24"></svg>
                  </div>
                  <span className="text-gray-700">Finish project proposal</span>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Progress</span>
                  <span className="font-medium text-gray-900">75%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full" style={{width: '75%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

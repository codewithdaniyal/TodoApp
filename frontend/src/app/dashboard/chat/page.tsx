import { Suspense } from 'react';
import ChatInterface from '@/components/chat-interface';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function ChatPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-8 shadow-inner">
        <div className="flex items-center">
          <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Task Assistant</h1>
            <p className="text-gray-600 mt-2">Interact with our AI assistant to manage your tasks using natural language</p>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100">
        <div className="h-[600px]">
          <Suspense fallback={<div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
              <p className="text-gray-600">Loading AI Assistant...</p>
            </div>
          </div>}>
            <ChatInterface />
          </Suspense>
        </div>
      </div>

      {/* Tips Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
          <h3 className="font-semibold text-blue-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Quick Actions
          </h3>
          <p className="text-sm text-blue-600 mt-1">Try: "Create a task to buy groceries"</p>
        </div>
        <div className="bg-green-50 rounded-xl p-4 border border-green-100">
          <h3 className="font-semibold text-green-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Task Management
          </h3>
          <p className="text-sm text-green-600 mt-1">Try: "Show me my tasks"</p>
        </div>
        <div className="bg-purple-50 rounded-xl p-4 border border-purple-100">
          <h3 className="font-semibold text-purple-800 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            Smart Commands
          </h3>
          <p className="text-sm text-purple-600 mt-1">Try: "Mark the first task as complete"</p>
        </div>
      </div>
    </div>
  );
}
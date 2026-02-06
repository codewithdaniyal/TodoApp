'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { sendChatMessage } from '@/lib/api/chat';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatInterface() {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated } = useAuth();

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading || !isAuthenticated) return;

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send to backend API
      const response = await sendChatMessage(inputValue.trim());
      
      // Add assistant response to UI
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      // Add error message to UI
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">Please sign in to use the chat feature.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl shadow-inner border border-gray-200">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 max-h-[400px]">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">How can I help you today?</h3>
            <p className="text-gray-600 mb-6">Ask me to create, update, or manage your tasks</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto">
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-700">"Create a task to buy groceries"</p>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-700">"Show me my tasks"</p>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-700">"Mark the first task as complete"</p>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <p className="text-sm text-gray-700">"Delete the meeting task"</p>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-5 py-3 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-br-none'
                    : 'bg-white text-gray-800 rounded-bl-none border border-gray-200 shadow-sm'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white rounded-b-2xl">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me to manage your tasks..."
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-3 text-center">
          Example: "Create a task to finish the report" or "Show me my tasks"
        </p>
      </form>
    </div>
  );
}
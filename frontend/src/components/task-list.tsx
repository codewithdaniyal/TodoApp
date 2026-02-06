/**
 * TaskList Component (T035)
 * Displays list of tasks with grid layout
 */

'use client'

import { type Task } from '@/lib/api/tasks'
import TaskItem from './task-item'

interface TaskListProps {
  tasks: Task[]
  onTaskUpdated: (task: Task) => void
  onTaskDeleted: (taskId: number) => void
}

export default function TaskList({ tasks, onTaskUpdated, onTaskDeleted }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="mx-auto w-24 h-24 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mb-6">
          <svg
            className="h-12 w-12 text-indigo-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="mt-4 text-xl font-semibold text-gray-900">No tasks yet</h3>
        <p className="mt-2 text-gray-600 max-w-md mx-auto">Get started by creating a new task. Your tasks will appear here.</p>
        <div className="mt-6 inline-flex items-center px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Try: "Create a task to buy groceries" in the AI Assistant
        </div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onTaskUpdated={onTaskUpdated}
          onTaskDeleted={onTaskDeleted}
        />
      ))}
    </div>
  )
}

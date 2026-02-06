/**
 * TaskItem Component (T036, T041, T042, T045)
 * Individual task display with checkbox, edit mode, and delete button
 */

'use client'

import { useState } from 'react'
import { updateTask, toggleComplete, deleteTask, type Task } from '@/lib/api/tasks'
import ConfirmDialog from './confirm-dialog'

interface TaskItemProps {
  task: Task
  onTaskUpdated: (task: Task) => void
  onTaskDeleted: (taskId: number) => void
}

export default function TaskItem({ task, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(task.title)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  // Handle completion toggle
  const handleToggleComplete = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const updatedTask = await toggleComplete(task.id)
      onTaskUpdated(updatedTask)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task')
    } finally {
      setIsLoading(false)
    }
  }

  // Handle title edit
  const handleEditSubmit = async () => {
    if (!editTitle.trim()) {
      setError('Task title cannot be empty')
      return
    }

    if (editTitle === task.title) {
      setIsEditing(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      const updatedTask = await updateTask(task.id, { title: editTitle.trim() })
      onTaskUpdated(updatedTask)
      setIsEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task')
    } finally {
      setIsLoading(false)
    }
  }

  // Handle delete
  const handleDelete = async () => {
    try {
      setIsLoading(true)
      setError(null)
      await deleteTask(task.id)
      onTaskDeleted(task.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task')
      setShowDeleteConfirm(false)
    } finally {
      setIsLoading(false)
    }
  }

  // Cancel edit
  const handleCancelEdit = () => {
    setEditTitle(task.title)
    setIsEditing(false)
    setError(null)
  }

  return (
    <div className={`rounded-xl p-5 transition-all duration-200 ${
      task.completed 
        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-100' 
        : 'bg-white border border-gray-200 hover:border-indigo-300 hover:shadow-md'
    }`}>
      <div className="flex items-start gap-4">
        {/* Completion Checkbox */}
        <button
          onClick={handleToggleComplete}
          disabled={isLoading}
          className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center mt-0.5 transition-all duration-200 ${
            task.completed
              ? 'bg-gradient-to-r from-green-500 to-emerald-600 border-green-500'
              : 'border-gray-300 hover:border-indigo-400'
          } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          aria-label={task.completed ? "Mark task as incomplete" : "Mark task as complete"}
        >
          {task.completed && (
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
            </svg>
          )}
        </button>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="space-y-3">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                disabled={isLoading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 shadow-sm"
                maxLength={500}
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={handleEditSubmit}
                  disabled={isLoading || !editTitle.trim()}
                  className="px-4 py-2 text-sm bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-lg hover:from-indigo-600 hover:to-indigo-700 disabled:opacity-50 transition-all duration-200 shadow-sm"
                >
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  disabled={isLoading}
                  className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:bg-gray-100 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <p
                className={`text-base font-medium ${
                  task.completed ? 'line-through text-gray-500' : 'text-gray-800'
                }`}
              >
                {task.title}
              </p>
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <span className="text-gray-500">
                  {new Date(task.created_at).toLocaleDateString()}
                </span>
                {task.completed && (
                  <span className="px-2.5 py-0.5 bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 rounded-full text-xs font-medium">
                    Completed
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {!isEditing && (
          <div className="flex gap-1">
            <button
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors disabled:opacity-50"
              aria-label="Edit task"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              aria-label="Delete task"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Task"
        message="Are you sure you want to delete this task? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        isLoading={isLoading}
      />
    </div>
  )
}

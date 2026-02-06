/**
 * Task API Client (T038, T043, T047)
 * Methods for CRUD operations on tasks
 */

'use client'

import { apiClient, type APIResponse } from './client'

export interface Task {
  id: number
  title: string
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TasksListResponse {
  data: {
    tasks: Task[]
    count: number
  }
  message: string
}

export interface TaskResponse {
  data: {
    task: Task
  }
  message: string
}

export interface CreateTaskData {
  title: string
}

export interface UpdateTaskData {
  title: string
}

/**
 * Get all tasks for authenticated user
 * @returns List of tasks ordered by newest first
 */
export async function getTasks(): Promise<Task[]> {
  const response = await apiClient.get<TasksListResponse>('/api/tasks')
  return response.data.tasks
}

/**
 * Create new task
 * @param data Task creation data (title)
 * @returns Newly created task
 */
export async function createTask(data: CreateTaskData): Promise<Task> {
  const response = await apiClient.post<TaskResponse>('/api/tasks', data)
  return response.data.task
}

/**
 * Update task title
 * @param id Task ID
 * @param data Updated task data (title)
 * @returns Updated task
 */
export async function updateTask(id: number, data: UpdateTaskData): Promise<Task> {
  const response = await apiClient.put<TaskResponse>(`/api/tasks/${id}`, data)
  return response.data.task
}

/**
 * Toggle task completion status
 * @param id Task ID
 * @returns Updated task with toggled completion status
 */
export async function toggleComplete(id: number): Promise<Task> {
  const response = await apiClient.patch<TaskResponse>(`/api/tasks/${id}/complete`)
  return response.data.task
}

/**
 * Delete task permanently
 * @param id Task ID
 */
export async function deleteTask(id: number): Promise<void> {
  await apiClient.delete<{ data: { task_id: number }, message: string }>(`/api/tasks/${id}`)
}

import { apiClient } from './client';

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  data: {
    message: string;
    actions: Array<{
      tool: string;
      arguments: Record<string, any>;
      result: Record<string, any>;
    }>;
    thread_id: string;
  };
  message: string;
}

/**
 * Send a chat message to the AI assistant
 */
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/chat', { message });
  return response;
}
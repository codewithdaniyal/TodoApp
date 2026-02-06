import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ChatInterface from '@/components/chat-interface';
import { useAuth } from '@/hooks/use-auth';
import { sendChatMessage } from '@/lib/api/chat';

// Mock the dependencies
vi.mock('@/hooks/use-auth');
vi.mock('@/lib/api/chat');

describe('ChatInterface', () => {
  beforeEach(() => {
    // Mock authenticated user
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should render the chat interface when authenticated', () => {
    render(<ChatInterface />);
    
    expect(screen.getByText('AI Task Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask me to manage your tasks...')).toBeInTheDocument();
  });

  it('should show authentication message when not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
    });

    render(<ChatInterface />);
    
    expect(screen.getByText('Please sign in to use the chat feature.')).toBeInTheDocument();
  });

  it('should send a message when submitted', async () => {
    const mockResponse = {
      data: {
        message: 'I have created the task for you.',
        actions: [],
        thread_id: 'thread_123',
      },
      message: 'Success',
    };
    
    (sendChatMessage as jest.Mock).mockResolvedValue(mockResponse);

    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText('Ask me to manage your tasks...');
    const button = screen.getByRole('button', { name: 'Send' });
    
    fireEvent.change(input, { target: { value: 'Create a task to buy groceries' } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith('Create a task to buy groceries');
      expect(screen.getByText('I have created the task for you.')).toBeInTheDocument();
    });
  });

  it('should handle errors gracefully', async () => {
    (sendChatMessage as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<ChatInterface />);
    
    const input = screen.getByPlaceholderText('Ask me to manage your tasks...');
    const button = screen.getByRole('button', { name: 'Send' });
    
    fireEvent.change(input, { target: { value: 'Create a task to buy groceries' } });
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('Sorry, I encountered an error processing your request. Please try again.')).toBeInTheDocument();
    });
  });
});
// Mock API client for testing purposes
export const mockApiClient = {
  post: jest.fn(),
};

// Actual API client
export { apiClient } from './client';
/**
 * API Configuration
 * 
 * This file centralizes API endpoint configuration for the React frontend.
 * Automatically uses the correct API URL based on environment.
 */

// Determine API base URL based on environment
const API_BASE_URL = (() => {
  // Check for environment variable (used in Vite)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // Development vs Production
  if (import.meta.env.MODE === 'production') {
    // Production: Use Render deployed API
    return 'https://wiki-quiz-api.onrender.com';
  }

  // Development: Use local backend
  return 'http://localhost:8000';
})();

export const config = {
  apiBaseUrl: API_BASE_URL,
  apiTimeout: 30000, // 30 seconds
};

/**
 * Get full API URL for a path
 * @param path API path (e.g., '/api/quizzes')
 * @returns Full URL
 */
export function getApiUrl(path: string): string {
  return `${config.apiBaseUrl}${path}`;
}

// Log configuration in development
if (import.meta.env.MODE === 'development') {
  console.log('[API Config] Using API URL:', config.apiBaseUrl);
}

export default config;

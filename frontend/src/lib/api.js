export const getAuthToken = () => localStorage.getItem('token');
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Warn in production if the env var is missing (means it'll hit localhost, which fails)
if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
  console.error(
    '[RewardIQ] VITE_API_URL is not set! API calls will fail. ' +
    'Set this env var in your Render frontend service settings.'
  );
}

export const apiFetch = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorMsg = 'An error occurred';
    try {
      const errorData = await response.json();
      if (typeof errorData.detail === 'string') {
        errorMsg = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMsg = errorData.detail.map(e => e.msg).join(', ');
      }
    } catch (e) {}
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

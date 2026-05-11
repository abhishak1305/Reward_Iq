export const getAuthToken = () => localStorage.getItem('token');
const getBaseUrl = () => {
  // If we are on localhost, always try to hit the local backend first
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/v1';
  }
  // Otherwise, use the production URL provided by Render/Vite
  return import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getBaseUrl();

// Warn in production if the env var is missing
if (import.meta.env.PROD && !import.meta.env.VITE_API_URL && window.location.hostname !== 'localhost') {
  console.warn('[RewardIQ] Running in production but VITE_API_URL is not set.');
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

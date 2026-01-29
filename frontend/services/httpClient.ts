import axios from 'axios';

// Token getter is injected by authService to avoid circular imports.
let getAccessToken: () => string | null = () => null;
export const setAuthTokenGetter = (fn: () => string | null) => {
  getAccessToken = fn;
};

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:5003',
  withCredentials: true,
  timeout: 10000, // 10s - fail fast on unresponsive backend
});

http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Refresh is handled by authService; rethrow if it fails.
        const { refreshToken } = await import('./authService');
        const newToken = await refreshToken();
        const { setAccessToken } = await import('./authService');
        setAccessToken(newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return http(originalRequest);
      } catch (refreshError) {
        const { clearAccessToken } = await import('./authService');
        clearAccessToken();
      }
    }
    return Promise.reject(error);
  }
);

export default http;

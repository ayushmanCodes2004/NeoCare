import axios from 'axios';

/**
 * Central Axios instance.
 *
 * REQUEST INTERCEPTOR:
 *   Automatically attaches JWT from localStorage to every request
 *   as: Authorization: Bearer <token>
 *
 * RESPONSE INTERCEPTOR:
 *   If any request gets a 401 (token expired or invalid):
 *   - Clear localStorage
 *   - Redirect to /login
 */
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('anc_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 globally
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('anc_token');
      localStorage.removeItem('anc_worker');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;

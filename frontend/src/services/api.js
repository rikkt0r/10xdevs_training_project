import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = process.env.REACT_APP_API_TIMEOUT || 30000;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response) {
      // Handle 401 Unauthorized
      if (error.response.status === 401 && !originalRequest._retry) {
        // Don't try to refresh if we're already on auth endpoints
        if (
          originalRequest.url.includes('/auth/login') ||
          originalRequest.url.includes('/auth/register') ||
          originalRequest.url.includes('/auth/refresh') ||
          originalRequest.url.includes('/auth/verify-email') ||
          originalRequest.url.includes('/auth/reset-password')
        ) {
          return Promise.reject(error);
        }

        if (isRefreshing) {
          // Queue this request while refresh is in progress
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return api(originalRequest);
            })
            .catch((err) => {
              return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const response = await api.post('/auth/refresh');
          const { access_token } = response.data.data;

          localStorage.setItem('access_token', access_token);
          api.defaults.headers.common.Authorization = `Bearer ${access_token}`;
          originalRequest.headers.Authorization = `Bearer ${access_token}`;

          processQueue(null, access_token);
          isRefreshing = false;

          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          isRefreshing = false;
          localStorage.removeItem('access_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      // Handle 403 Forbidden (account suspended or email not verified)
      if (error.response.status === 403) {
        const errorData = error.response.data?.error;
        if (errorData?.code === 'ACCOUNT_SUSPENDED' || errorData?.code === 'EMAIL_NOT_VERIFIED') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;

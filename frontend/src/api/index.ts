import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 token
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

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API 方法
export const authAPI = {
  register: (data: { username: string; email: string; password: string; user_type?: string }) =>
    api.post('/api/v1/auth/register', data),

  login: (username: string, password: string) =>
    api.post('/api/v1/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getMe: () => api.get('/api/v1/auth/me'),
};

export const casesAPI = {
  search: (data: { query: string; filters?: any; page?: number; page_size?: number }) =>
    api.post('/api/v1/cases/search', data),

  getCase: (id: number) => api.get(`/api/v1/cases/${id}`),

  analyzeCase: (id: number) => api.post(`/api/v1/cases/${id}/analyze`),

  createCase: (data: any) => api.post('/api/v1/cases/', data),
};

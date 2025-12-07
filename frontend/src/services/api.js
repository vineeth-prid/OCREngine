import axios from 'axios';

// Detect if running in preview/production or local environment
const getApiBaseUrl = () => {
  // If explicit env var is set, use it
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // If running on localhost, use port 8001
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8001';
  }
  
  // For preview/production environments, use same origin (backend is on /api route)
  return window.location.origin;
};

const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getCurrentUser: () => api.get('/api/auth/me'),
};

export const tenantAPI = {
  getMyTenant: () => api.get('/api/tenants/me'),
  updateMyTenant: (data) => api.put('/api/tenants/me', data),
  getSubscription: () => api.get('/api/tenants/me/subscription'),
  getUsage: () => api.get('/api/tenants/me/usage'),
};

export const schemaAPI = {
  create: (data) => api.post('/api/schemas/', data),
  list: (params) => api.get('/api/schemas/', { params }),
  get: (id) => api.get(`/api/schemas/${id}`),
  update: (id, data) => api.put(`/api/schemas/${id}`, data),
  delete: (id) => api.delete(`/api/schemas/${id}`),
  addField: (schemaId, data) => api.post(`/api/schemas/${schemaId}/fields`, data),
  removeField: (schemaId, fieldId) => api.delete(`/api/schemas/${schemaId}/fields/${fieldId}`),
};

export const documentAPI = {
  upload: (formData) => api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  list: (params) => api.get('/api/documents/', { params }),
  get: (id) => api.get(`/api/documents/${id}`),
  process: (id) => api.post(`/api/documents/${id}/process`),
  delete: (id) => api.delete(`/api/documents/${id}`),
  getLogs: (id) => api.get(`/api/documents/${id}/logs`),
  getFields: (id) => api.get(`/api/documents/${id}/fields`),
};

export const userAPI = {
  list: (params) => api.get('/api/users/', { params }),
  get: (id) => api.get(`/api/users/${id}`),
  update: (id, data) => api.put(`/api/users/${id}`, data),
  delete: (id) => api.delete(`/api/users/${id}`),
  getRoles: (id) => api.get(`/api/users/${id}/roles`),
  assignRole: (id, data) => api.post(`/api/users/${id}/roles`, data),
};

export const roleAPI = {
  list: () => api.get('/api/roles/'),
  get: (id) => api.get(`/api/roles/${id}`),
};

export const adminAPI = {
  getStats: () => api.get('/api/admin/stats'),
  listAllTenants: (params) => api.get('/api/admin/tenants', { params }),
  getConfig: (key) => api.get(`/api/admin/config/${key}`),
  listConfigs: () => api.get('/api/admin/config'),
  createConfig: (data) => api.post('/api/admin/config', data),
  updateConfig: (key, data) => api.put(`/api/admin/config/${key}`, data),
};

export const llmAPI = {
  getStatus: () => api.get('/api/llm/status'),
  getConfig: () => api.get('/api/llm/config'),
  updateConfig: (data) => api.post('/api/llm/config', data),
  downloadModel: (modelName) => api.post('/api/llm/download-model', null, { params: { model_name: modelName } }),
  testConnection: (modelType) => api.post('/api/llm/test-connection', null, { params: { model_type: modelType } }),
};

export default api;

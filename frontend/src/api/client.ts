import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session API
export const sessionApi = {
  create: () => api.post('/sessions'),
  get: (id: string) => api.get(`/sessions/${id}`),
  delete: (id: string) => api.delete(`/sessions/${id}`),
  reset: (id: string) => api.post(`/sessions/${id}/reset`),
  query: (id: string, sql: string) => api.post(`/sessions/${id}/query`, { sql }),
  getHistory: (id: string) => api.get(`/sessions/${id}/history`),
};

// Schema API
export const schemaApi = {
  getAll: (sessionId: string) => api.get(`/sessions/${sessionId}/schema`),
  getTable: (sessionId: string, tableName: string) =>
    api.get(`/sessions/${sessionId}/schema/${tableName}`),
  getPreview: (sessionId: string, tableName: string, limit = 10) =>
    api.get(`/sessions/${sessionId}/schema/${tableName}/preview?limit=${limit}`),
};

// Challenge API
export const challengeApi = {
  list: () => api.get('/challenges'),
  get: (id: string) => api.get(`/challenges/${id}`),
  setup: (id: string, sessionId: string) =>
    api.post(`/challenges/${id}/setup?session_id=${sessionId}`),
  submit: (id: string, sessionId: string, sql: string, hintsUsed = 0) =>
    api.post(`/challenges/${id}/submit?session_id=${sessionId}`, { sql, hints_used: hintsUsed }),
  getHint: (id: string, hintIndex: number) =>
    api.get(`/challenges/${id}/hints/${hintIndex}`),
};

// Health check
export const healthApi = {
  check: () => api.get('/health'),
  info: () => api.get('/info'),
};

export default api;

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Workflows
export const workflowAPI = {
    list: () => api.get('/workflows/'),
    get: (id) => api.get(`/workflows/${id}`),
    create: (data) => api.post('/workflows/', data),
    update: (id, data) => api.put(`/workflows/${id}`, data),
    delete: (id) => api.delete(`/workflows/${id}`),
    validate: (id) => api.post(`/workflows/${id}/validate`),
};

// Documents
export const documentAPI = {
    list: () => api.get('/documents/'),
    upload: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    delete: (id) => api.delete(`/documents/${id}`),
};

// Chat
export const chatAPI = {
    execute: (data) => api.post('/chat/execute', data),
    getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
};

export default api;

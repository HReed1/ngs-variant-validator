import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_FRONTEND_API_KEY;

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Inject Auth Header via Interceptor
apiClient.interceptors.request.use((config) => {
    if (API_KEY) {
        config.headers['X-API-Key'] = API_KEY;
    }
    return config;
});
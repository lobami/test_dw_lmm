import axios from 'axios';

// Read API URL from Vite env (VITE_API_URL) when building for production.
// Falls back to localhost for local development.
const API_URL = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    timeout: 5000,
    withCredentials: true,
});

// Attach token from localStorage if present
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
});

// Silent refresh flow on 401 with a request queue.
let isRefreshing = false as boolean;
let failedQueue: Array<{ resolve: (value?: any) => void; reject: (err: any) => void; config: any }> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            if (token && prom.config.headers) prom.config.headers['Authorization'] = `Bearer ${token}`;
            prom.resolve(api(prom.config));
        }
    });
    failedQueue = [];
};

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        const status = error?.response?.status;

        if (status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            // we rely on httpOnly refresh cookie. If there's no access token, attempt refresh.

            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject, config: originalRequest });
                });
            }

            isRefreshing = true;

            try {
                const resp = await api.post('/auth/refresh');
                const newAccess = resp.data.access_token;
                try {
                    localStorage.setItem('access_token', newAccess);
                } catch (e) {}
                processQueue(null, newAccess);
                isRefreshing = false;
                if (originalRequest.headers) originalRequest.headers['Authorization'] = `Bearer ${newAccess}`;
                return api(originalRequest);
            } catch (err) {
                processQueue(err, null);
                isRefreshing = false;
                window.dispatchEvent(new CustomEvent('auth:expired'));
                return Promise.reject(err);
            }
        }

        return Promise.reject(error);
    }
);

export default api;

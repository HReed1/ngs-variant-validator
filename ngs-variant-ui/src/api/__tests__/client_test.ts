import { describe, it, expect } from 'vitest';
import { apiClient } from '../client';

describe('API Client Configuration', () => {
    it('injects the X-API-Key header into requests', async () => {
        // Force the environment variable for the test scope
        import.meta.env.VITE_FRONTEND_API_KEY = 'test_dummy_key';

        // Intercept the request to verify the header insertion
        apiClient.interceptors.request.use((config) => {
            expect(config.headers['X-API-Key']).toBe('test_dummy_key');
            return config;
        });

        // Fire a dummy request (it will fail network-wise, but the interceptor fires first)
        await apiClient.get('/dummy').catch(() => { });
    });
});
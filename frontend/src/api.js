import axios from 'axios';

const API_BASE_URL = 'https://security-audit-tool-1.onrender.com';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const generateAudit = async (url, token = null) => {
    try {
        const config = {
            responseType: 'blob',
            headers: {}
        };

        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await api.post('/generate-audit', { url }, config);
        return response.data;
    } catch (error) {
        if (error.response) {
            throw new Error(error.response.data.detail || 'Audit generation failed');
        } else if (error.request) {
            throw new Error('No response from server. Is the backend running?');
        } else {
            throw new Error(error.message);
        }
    }
};


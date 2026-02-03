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
            headers: {}
        };

        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await api.post('/generate-audit', { url }, config);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || error.message);
    }
};

export const downloadPDF = async (filename) => {
    try {
        const response = await api.get(`/download-pdf/${filename}`, {
            responseType: 'blob'
        });
        return response.data;
    } catch (error) {
        throw new Error("Failed to download report. It may have expired.");
    }
};


import axios from 'axios';

const API_BASE_URL = 'https://security-audit-tool-1.onrender.com';
// const API_BASE_URL = 'http://localhost:8000'; // USE THIS FOR LOCAL TESTING

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

export const downloadPDF = async (filename, token) => {
    try {
        const config = {
            responseType: 'blob'
        };

        if (token) {
            config.headers = {
                'Authorization': `Bearer ${token}`
            };
        }

        const response = await api.get(`/download-pdf/${filename}`, config);
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            throw new Error("Please sign in to download PDF reports.");
        }
        throw new Error("Failed to download report. It may have expired.");
    }
};
export const deleteScan = async (scanId, token) => {
    try {
        const response = await api.delete(`/delete-scan/${scanId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || "Failed to delete scan.");
    }
};
export const toggleAutomation = async (hostname, enable, token) => {
    try {
        const response = await api.post('/toggle-automation', { hostname, enable }, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || "Failed to toggle automation.");
    }
};

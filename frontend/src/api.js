import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const generateAudit = async (url) => {
    try {
        const response = await api.post('/generate-audit', { url }, {
            responseType: 'blob', // Important for PDF download
        });
        return response.data;
    } catch (error) {
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            throw new Error(error.response.data.detail || 'Audit generation failed');
        } else if (error.request) {
            // The request was made but no response was received
            throw new Error('No response from server. Is the backend running?');
        } else {
            // Something happened in setting up the request that triggered an Error
            throw new Error(error.message);
        }
    }
};

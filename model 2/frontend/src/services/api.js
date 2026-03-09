import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const submitTicket = async (formData) => {
    return axios.post(`${API_BASE}/intake/submit`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    });
};

export const fetchAllTickets = async () => {
    return axios.get(`${API_BASE}/tickets/`);
};

export const fetchCitizenTickets = async (citizenId) => {
    return axios.get(`${API_BASE}/tickets/citizen/${citizenId}`);
};

export const updateTicketStatus = async (ticketId, status) => {
    return axios.put(`${API_BASE}/tickets/${ticketId}/status?status=${status}`);
};

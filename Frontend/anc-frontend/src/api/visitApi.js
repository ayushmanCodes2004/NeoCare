import api from './axiosInstance';

// POST /api/anc/register-visit
export const registerVisit = (data) => api.post('/api/anc/register-visit', data).then(r => r.data);

// GET /api/anc/visits/:visitId
export const getVisit = (id) => api.get(`/api/anc/visits/${id}`).then(r => r.data);

// GET /api/anc/patients/:patientId/visits
export const getPatientVisits = (id) => api.get(`/api/anc/patients/${id}/visits`).then(r => r.data);

// GET /api/anc/visits/high-risk
export const getHighRisk = () => api.get('/api/anc/visits/high-risk').then(r => r.data);

// GET /api/anc/visits/critical
export const getCritical = () => api.get('/api/anc/visits/critical').then(r => r.data);

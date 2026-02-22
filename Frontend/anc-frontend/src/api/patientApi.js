import api from './axiosInstance';

// POST /api/patients
export const createPatient = (data) => api.post('/api/patients', data).then(r => r.data);

// GET /api/patients
export const getPatients = () => api.get('/api/patients').then(r => r.data);

// GET /api/patients/:id
export const getPatient = (id) => api.get(`/api/patients/${id}`).then(r => r.data);

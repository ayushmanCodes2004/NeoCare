import api from './axiosInstance';

// GET /api/consultations/queue
export const getQueue = () => api.get('/api/consultations/queue').then(r => r.data);

// GET /api/consultations/:id
export const getConsult = (id) => api.get(`/api/consultations/${id}`).then(r => r.data);

// POST /api/consultations/:id/accept
export const acceptConsult = (id) => api.post(`/api/consultations/${id}/accept`).then(r => r.data);

// POST /api/consultations/:id/start-call
export const startCall = (id) => api.post(`/api/consultations/${id}/start-call`).then(r => r.data);

// POST /api/consultations/:id/complete
// body: { doctorNotes, diagnosis, actionPlan }
export const completeConsult = (id, data) => api.post(`/api/consultations/${id}/complete`, data).then(r => r.data);

// GET /api/consultations/my-history
export const getHistory = () => api.get('/api/consultations/my-history').then(r => r.data);

// GET /api/consultations/patient/:patientId
export const getPatientConsults = (patientId) => api.get(`/api/consultations/patient/${patientId}`).then(r => r.data);

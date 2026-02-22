import api from './axiosInstance';

// POST /api/doctor/auth/signup
export const doctorSignup = (data) => api.post('/api/doctor/auth/signup', data).then(r => r.data);

// POST /api/doctor/auth/login
export const doctorLogin = (data) => api.post('/api/doctor/auth/login', data).then(r => r.data);

// GET /api/doctor/auth/me
export const doctorMe = () => api.get('/api/doctor/auth/me').then(r => r.data);

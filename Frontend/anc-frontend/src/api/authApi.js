import api from './axiosInstance';

// POST /api/auth/signup → { fullName, phone, email, password, healthCenter, district }
export const workerSignup = (data) => api.post('/api/auth/signup', data).then(r => r.data);

// POST /api/auth/login → { phone, password }
export const workerLogin = (data) => api.post('/api/auth/login', data).then(r => r.data);

// GET /api/auth/me
export const workerMe = () => api.get('/api/auth/me').then(r => r.data);

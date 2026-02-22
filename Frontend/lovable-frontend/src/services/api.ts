import axios from 'axios';

const API_BASE = 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('anc_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Worker Auth
export const workerSignup = (data: any) => api.post('/api/auth/signup', data);
export const workerLogin = (data: any) => api.post('/api/auth/login', data);
export const getWorkerProfile = () => api.get('/api/auth/me');

// Doctor Auth
export const doctorSignup = (data: any) => api.post('/api/doctor/auth/signup', data);
export const doctorLogin = (data: any) => api.post('/api/doctor/auth/login', data);
export const getDoctorProfile = () => api.get('/api/doctor/auth/me');

// Patients
export const createPatient = (data: any) => api.post('/api/patients', data);
export const getPatients = () => api.get('/api/patients');
export const getPatient = (id: string) => api.get(`/api/patients/${id}`);

// ANC Visits
export const registerVisit = (data: any) => api.post('/api/anc/register-visit', data);
export const getVisit = (id: string) => api.get(`/api/anc/visits/${id}`);
export const getPatientVisits = (patientId: string) => api.get(`/api/anc/patients/${patientId}/visits`);
export const getHighRiskVisits = () => api.get('/api/anc/visits/high-risk');
export const getCriticalVisits = () => api.get('/api/anc/visits/critical');

// Consultations
export const getConsultationQueue = () => api.get('/api/consultations/queue');
export const getConsultation = (id: string) => api.get(`/api/consultations/${id}`);
export const acceptConsultation = (id: string) => api.post(`/api/consultations/${id}/accept`);
export const startCall = (id: string) => api.post(`/api/consultations/${id}/start-call`);
export const completeConsultation = (id: string, notes: any) => api.post(`/api/consultations/${id}/complete`, notes);
export const getDoctorHistory = () => api.get('/api/consultations/my-history');

export default api;

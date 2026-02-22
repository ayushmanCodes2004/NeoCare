#!/bin/bash

# ANC Portal Frontend - API Layer Setup
# Creates all API files, contexts, hooks, and routes

set -e
BASE_DIR="Frontend/anc-frontend"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔌 Creating API layer...${NC}"

# ============================================
# API FILES
# ============================================

# axiosInstance.js
cat > "$BASE_DIR/src/api/axiosInstance.js" << 'EOF'
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('anc_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
}, err => Promise.reject(err));

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;
EOF

# authApi.js
cat > "$BASE_DIR/src/api/authApi.js" << 'EOF'
import api from './axiosInstance';
export const workerSignup = d => api.post('/api/auth/signup', d).then(r => r.data);
export const workerLogin  = d => api.post('/api/auth/login',  d).then(r => r.data);
export const workerMe     = () => api.get('/api/auth/me').then(r => r.data);
EOF

# doctorApi.js
cat > "$BASE_DIR/src/api/doctorApi.js" << 'EOF'
import api from './axiosInstance';
export const doctorSignup = d => api.post('/api/doctor/auth/signup', d).then(r => r.data);
export const doctorLogin  = d => api.post('/api/doctor/auth/login',  d).then(r => r.data);
export const doctorMe     = () => api.get('/api/doctor/auth/me').then(r => r.data);
EOF

# patientApi.js
cat > "$BASE_DIR/src/api/patientApi.js" << 'EOF'
import api from './axiosInstance';
export const createPatient  = d  => api.post('/api/patients', d).then(r => r.data);
export const getPatients    = () => api.get('/api/patients').then(r => r.data);
export const getPatient     = id => api.get(`/api/patients/${id}`).then(r => r.data);
EOF

# visitApi.js
cat > "$BASE_DIR/src/api/visitApi.js" << 'EOF'
import api from './axiosInstance';
export const registerVisit    = d  => api.post('/api/anc/register-visit', d).then(r => r.data);
export const getVisit         = id => api.get(`/api/anc/visits/${id}`).then(r => r.data);
export const getPatientVisits = id => api.get(`/api/anc/patients/${id}/visits`).then(r => r.data);
export const getHighRisk      = () => api.get('/api/anc/visits/high-risk').then(r => r.data);
export const getCritical      = () => api.get('/api/anc/visits/critical').then(r => r.data);
EOF

# consultationApi.js
cat > "$BASE_DIR/src/api/consultationApi.js" << 'EOF'
import api from './axiosInstance';
export const getQueue      = () => api.get('/api/consultations/queue').then(r => r.data);
export const getConsult    = id => api.get(`/api/consultations/${id}`).then(r => r.data);
export const acceptConsult = id => api.post(`/api/consultations/${id}/accept`).then(r => r.data);
export const startCall     = id => api.post(`/api/consultations/${id}/start-call`).then(r => r.data);
export const completeConsult = (id,d) => api.post(`/api/consultations/${id}/complete`, d).then(r => r.data);
export const getHistory    = () => api.get('/api/consultations/my-history').then(r => r.data);
export const getPatientConsults = pid => api.get(`/api/consultations/patient/${pid}`).then(r => r.data);
EOF

echo -e "${GREEN}✓ API files created${NC}"

# ============================================
# CONTEXT FILES
# ============================================
echo -e "${BLUE}🔐 Creating context files...${NC}"

# AuthContext.jsx
cat > "$BASE_DIR/src/context/AuthContext.jsx" << 'EOF'
import { createContext, useState, useEffect, useCallback } from 'react';
import { workerLogin, workerSignup } from '../api/authApi';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [ready, setReady]     = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('anc_token');
    const stored = localStorage.getItem('anc_user');
    const role   = localStorage.getItem('anc_role');
    if (token && stored && role === 'WORKER') {
      try { setUser(JSON.parse(stored)); } catch { localStorage.clear(); }
    }
    setReady(true);
  }, []);

  const persist = (data) => {
    const { token, ...info } = data;
    localStorage.setItem('anc_token', token);
    localStorage.setItem('anc_user',  JSON.stringify(info));
    localStorage.setItem('anc_role',  'WORKER');
    setUser(info);
  };

  const login  = useCallback(async (phone, password) => {
    const r = await workerLogin({ phone, password }); persist(r); return r;
  }, []);

  const signup = useCallback(async (d) => {
    const r = await workerSignup(d); persist(r); return r;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear(); setUser(null); window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, isAuth: !!user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
EOF

# DoctorAuthContext.jsx
cat > "$BASE_DIR/src/context/DoctorAuthContext.jsx" << 'EOF'
import { createContext, useState, useEffect, useCallback } from 'react';
import { doctorLogin, doctorSignup } from '../api/doctorApi';

export const DoctorAuthContext = createContext(null);

export function DoctorAuthProvider({ children }) {
  const [doctor, setDoctor] = useState(null);
  const [ready,  setReady]  = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('anc_token');
    const stored = localStorage.getItem('anc_user');
    const role   = localStorage.getItem('anc_role');
    if (token && stored && role === 'DOCTOR') {
      try { setDoctor(JSON.parse(stored)); } catch { localStorage.clear(); }
    }
    setReady(true);
  }, []);

  const persist = (data) => {
    const { token, ...info } = data;
    localStorage.setItem('anc_token', token);
    localStorage.setItem('anc_user',  JSON.stringify(info));
    localStorage.setItem('anc_role',  'DOCTOR');
    setDoctor(info);
  };

  const login  = useCallback(async (phone, password) => {
    const r = await doctorLogin({ phone, password }); persist(r); return r;
  }, []);

  const signup = useCallback(async (d) => {
    const r = await doctorSignup(d); persist(r); return r;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear(); setDoctor(null); window.location.href = '/doctor/login';
  }, []);

  return (
    <DoctorAuthContext.Provider value={{ doctor, ready, isAuth: !!doctor, login, signup, logout }}>
      {children}
    </DoctorAuthContext.Provider>
  );
}
EOF

echo -e "${GREEN}✓ Context files created${NC}"

# ============================================
# HOOKS
# ============================================
echo -e "${BLUE}🪝 Creating hooks...${NC}"

# useAuth.js
cat > "$BASE_DIR/src/hooks/useAuth.js" << 'EOF'
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
export const useAuth = () => useContext(AuthContext);
EOF

# useDoctorAuth.js
cat > "$BASE_DIR/src/hooks/useDoctorAuth.js" << 'EOF'
import { useContext } from 'react';
import { DoctorAuthContext } from '../context/DoctorAuthContext';
export const useDoctorAuth = () => useContext(DoctorAuthContext);
EOF

# useApi.js
cat > "$BASE_DIR/src/hooks/useApi.js" << 'EOF'
import { useState, useCallback } from 'react';

export function useApi(fn) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const run = useCallback(async (...args) => {
    setLoading(true); setError(null);
    try {
      const r = await fn(...args); setData(r); return r;
    } catch (e) {
      const msg = e.response?.data?.message || e.message || 'Request failed';
      setError(msg); throw e;
    } finally { setLoading(false); }
  }, [fn]);

  return { data, loading, error, run, setData };
}
EOF

echo -e "${GREEN}✓ Hooks created${NC}"

# ============================================
# ROUTES
# ============================================
echo -e "${BLUE}🛣️  Creating route guards...${NC}"

# WorkerRoute.jsx
cat > "$BASE_DIR/src/routes/WorkerRoute.jsx" << 'EOF'
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Spinner from '../components/ui/Spinner';

export default function WorkerRoute() {
  const { isAuth, ready } = useAuth();
  if (!ready) return <div className="flex h-screen items-center justify-center"><Spinner lg /></div>;
  return isAuth ? <Outlet /> : <Navigate to="/login" replace />;
}
EOF

# DoctorRoute.jsx
cat > "$BASE_DIR/src/routes/DoctorRoute.jsx" << 'EOF'
import { Navigate, Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../hooks/useDoctorAuth';
import Spinner from '../components/ui/Spinner';

export default function DoctorRoute() {
  const { isAuth, ready } = useDoctorAuth();
  if (!ready) return <div className="flex h-screen items-center justify-center"><Spinner lg /></div>;
  return isAuth ? <Outlet /> : <Navigate to="/doctor/login" replace />;
}
EOF

echo -e "${GREEN}✓ Route guards created${NC}"
echo -e "${GREEN}✅ API layer complete!${NC}"
EOF

# ANC Portal — Professional React Frontend
## Complete Implementation: All Endpoints · Both Portals · JWT Auth · Video Teleconsultation

**Stack:** React 18 · Vite · React Router v6 · Axios · React Hook Form · Recharts · @daily-co/daily-js · Lucide React

**Aesthetic:** Clinical precision — deep navy/slate, teal signal accents, sharp data density, medical-grade trust

---

## All Routes Covered

### Worker Portal (`/`)
| Route | Page | Endpoints Hit |
|-------|------|---------------|
| `/login` | Worker Login | `POST /api/auth/login` |
| `/signup` | Worker Signup | `POST /api/auth/signup` |
| `/dashboard` | Worker Dashboard | `GET /api/patients`, `GET /api/anc/visits/high-risk`, `GET /api/anc/visits/critical` |
| `/patients` | Patient List | `GET /api/patients` |
| `/patients/new` | Register Patient | `POST /api/patients` |
| `/patients/:id` | Patient Detail | `GET /api/patients/:id`, `GET /api/anc/patients/:id/visits`, `GET /api/consultations/patient/:id` |
| `/visits/new/:patientId` | ANC Visit Form (7 steps) | `POST /api/anc/register-visit` |
| `/visits/:visitId` | Visit Result | `GET /api/anc/visits/:visitId` |

### Doctor Portal (`/doctor`)
| Route | Page | Endpoints Hit |
|-------|------|---------------|
| `/doctor/login` | Doctor Login | `POST /api/doctor/auth/login` |
| `/doctor/signup` | Doctor Signup | `POST /api/doctor/auth/signup` |
| `/doctor/dashboard` | Doctor Dashboard | `GET /api/consultations/queue`, `GET /api/consultations/my-history` |
| `/doctor/queue` | Priority Queue | `GET /api/consultations/queue`, `POST /api/consultations/:id/accept` |
| `/doctor/consultations/:id` | Full Case View + Video Call | `GET /api/consultations/:id`, `POST /api/consultations/:id/start-call`, `POST /api/consultations/:id/complete` |
| `/doctor/history` | Past Consultations | `GET /api/consultations/my-history` |

---

## Complete Project Structure

```
anc-frontend/
├── index.html
├── vite.config.js
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── .env
│
└── src/
    ├── main.jsx
    ├── App.jsx
    │
    ├── api/
    │   ├── axiosInstance.js
    │   ├── authApi.js
    │   ├── patientApi.js
    │   ├── visitApi.js
    │   ├── doctorApi.js
    │   └── consultationApi.js
    │
    ├── context/
    │   ├── AuthContext.jsx          ← Worker auth
    │   └── DoctorAuthContext.jsx    ← Doctor auth
    │
    ├── hooks/
    │   ├── useAuth.js
    │   ├── useDoctorAuth.js
    │   └── useApi.js
    │
    ├── routes/
    │   ├── WorkerRoute.jsx
    │   └── DoctorRoute.jsx
    │
    ├── components/
    │   ├── ui/
    │   │   ├── Input.jsx
    │   │   ├── Button.jsx
    │   │   ├── RiskBadge.jsx
    │   │   ├── StatCard.jsx
    │   │   ├── Spinner.jsx
    │   │   ├── Toast.jsx
    │   │   ├── Modal.jsx
    │   │   └── EmptyState.jsx
    │   ├── layout/
    │   │   ├── WorkerLayout.jsx
    │   │   └── DoctorLayout.jsx
    │   ├── charts/
    │   │   └── RiskDonutChart.jsx
    │   ├── visits/
    │   │   ├── StepWizard.jsx
    │   │   ├── RiskReport.jsx
    │   │   └── ConfidenceBar.jsx
    │   └── video/
    │       └── VideoRoom.jsx
    │
    └── pages/
        ├── worker/
        │   ├── LoginPage.jsx
        │   ├── SignupPage.jsx
        │   ├── DashboardPage.jsx
        │   ├── PatientListPage.jsx
        │   ├── PatientCreatePage.jsx
        │   ├── PatientDetailPage.jsx
        │   ├── VisitFormPage.jsx
        │   └── VisitResultPage.jsx
        └── doctor/
            ├── DoctorLoginPage.jsx
            ├── DoctorSignupPage.jsx
            ├── DoctorDashboardPage.jsx
            ├── QueuePage.jsx
            ├── ConsultationPage.jsx
            └── HistoryPage.jsx
```

---

## package.json

```json
{
  "name": "anc-portal",
  "version": "2.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev":     "vite",
    "build":   "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react":             "^18.3.1",
    "react-dom":         "^18.3.1",
    "react-router-dom":  "^6.23.1",
    "axios":             "^1.7.2",
    "react-hook-form":   "^7.51.5",
    "recharts":          "^2.12.7",
    "lucide-react":      "^0.395.0",
    "date-fns":          "^3.6.0",
    "@daily-co/daily-js": "^0.70.0",
    "clsx":              "^2.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite":          "^5.3.1",
    "tailwindcss":   "^3.4.4",
    "postcss":       "^8.4.39",
    "autoprefixer":  "^10.4.19"
  }
}
```

---

## vite.config.js

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
});
```

---

## tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['"DM Sans"', 'sans-serif'],
        display: ['"Syne"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        navy:  { 950: '#050d1a', 900: '#0a1628', 800: '#0f2044', 700: '#1a3560', 600: '#234a80' },
        teal:  { 400: '#2dd4bf', 500: '#14b8a6', 600: '#0d9488' },
        risk: {
          critical: '#ef4444',
          high:     '#f97316',
          medium:   '#eab308',
          low:      '#22c55e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in':    'fadeIn 0.4s ease-out',
        'slide-up':   'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 },               to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
};
```

---

## postcss.config.js

```js
export default { plugins: { tailwindcss: {}, autoprefixer: {} } };
```

---

## .env

```
VITE_API_BASE=http://localhost:8080
```

---

## index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ANC Portal — Maternal Health Risk System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

---

## src/main.jsx

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
);
```

---

## src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  *, *::before, *::after { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    @apply bg-navy-950 text-slate-100 font-sans antialiased;
    margin: 0;
  }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { @apply bg-navy-900; }
  ::-webkit-scrollbar-thumb { @apply bg-navy-700 rounded-full; }
  ::-webkit-scrollbar-thumb:hover { @apply bg-navy-600; }
}

@layer components {
  .glass {
    @apply bg-white/5 backdrop-blur-sm border border-white/10;
  }
  .glass-card {
    @apply bg-navy-900 border border-white/10 rounded-2xl;
  }
  .section-label {
    @apply text-xs font-mono uppercase tracking-widest text-teal-400 mb-1;
  }
  .risk-critical { @apply text-risk-critical bg-risk-critical/10 border-risk-critical/30; }
  .risk-high     { @apply text-risk-high    bg-risk-high/10    border-risk-high/30; }
  .risk-medium   { @apply text-risk-medium  bg-risk-medium/10  border-risk-medium/30; }
  .risk-low      { @apply text-risk-low     bg-risk-low/10     border-risk-low/30; }
}
```

---

## src/api/axiosInstance.js

```js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Attach JWT on every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('anc_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
}, err => Promise.reject(err));

// Global 401 handler
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
```

---

## src/api/authApi.js

```js
import api from './axiosInstance';
// POST /api/auth/signup  → { fullName, phone, email, password, healthCenter, district }
export const workerSignup = d => api.post('/api/auth/signup', d).then(r => r.data);
// POST /api/auth/login   → { phone, password }
export const workerLogin  = d => api.post('/api/auth/login',  d).then(r => r.data);
// GET  /api/auth/me
export const workerMe     = () => api.get('/api/auth/me').then(r => r.data);
```

---

## src/api/patientApi.js

```js
import api from './axiosInstance';
// POST /api/patients
export const createPatient  = d  => api.post('/api/patients', d).then(r => r.data);
// GET  /api/patients
export const getPatients    = () => api.get('/api/patients').then(r => r.data);
// GET  /api/patients/:id
export const getPatient     = id => api.get(`/api/patients/${id}`).then(r => r.data);
```

---

## src/api/visitApi.js

```js
import api from './axiosInstance';
// POST /api/anc/register-visit
export const registerVisit    = d  => api.post('/api/anc/register-visit', d).then(r => r.data);
// GET  /api/anc/visits/:visitId
export const getVisit         = id => api.get(`/api/anc/visits/${id}`).then(r => r.data);
// GET  /api/anc/patients/:patientId/visits
export const getPatientVisits = id => api.get(`/api/anc/patients/${id}/visits`).then(r => r.data);
// GET  /api/anc/visits/high-risk
export const getHighRisk      = () => api.get('/api/anc/visits/high-risk').then(r => r.data);
// GET  /api/anc/visits/critical
export const getCritical      = () => api.get('/api/anc/visits/critical').then(r => r.data);
```

---

## src/api/doctorApi.js

```js
import api from './axiosInstance';
// POST /api/doctor/auth/signup
export const doctorSignup = d => api.post('/api/doctor/auth/signup', d).then(r => r.data);
// POST /api/doctor/auth/login
export const doctorLogin  = d => api.post('/api/doctor/auth/login',  d).then(r => r.data);
// GET  /api/doctor/auth/me
export const doctorMe     = () => api.get('/api/doctor/auth/me').then(r => r.data);
```

---

## src/api/consultationApi.js

```js
import api from './axiosInstance';
// GET  /api/consultations/queue
export const getQueue      = () => api.get('/api/consultations/queue').then(r => r.data);
// GET  /api/consultations/:id
export const getConsult    = id => api.get(`/api/consultations/${id}`).then(r => r.data);
// POST /api/consultations/:id/accept
export const acceptConsult = id => api.post(`/api/consultations/${id}/accept`).then(r => r.data);
// POST /api/consultations/:id/start-call
export const startCall     = id => api.post(`/api/consultations/${id}/start-call`).then(r => r.data);
// POST /api/consultations/:id/complete  body: { doctorNotes, diagnosis, actionPlan }
export const completeConsult = (id,d) => api.post(`/api/consultations/${id}/complete`, d).then(r => r.data);
// GET  /api/consultations/my-history
export const getHistory    = () => api.get('/api/consultations/my-history').then(r => r.data);
// GET  /api/consultations/patient/:patientId
export const getPatientConsults = pid => api.get(`/api/consultations/patient/${pid}`).then(r => r.data);
```

---

## src/context/AuthContext.jsx

```jsx
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
```

---

## src/context/DoctorAuthContext.jsx

```jsx
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
```

---

## src/hooks/useAuth.js

```js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
export const useAuth = () => useContext(AuthContext);
```

---

## src/hooks/useDoctorAuth.js

```js
import { useContext } from 'react';
import { DoctorAuthContext } from '../context/DoctorAuthContext';
export const useDoctorAuth = () => useContext(DoctorAuthContext);
```

---

## src/hooks/useApi.js

```js
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
```

---

## src/routes/WorkerRoute.jsx

```jsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Spinner from '../components/ui/Spinner';

export default function WorkerRoute() {
  const { isAuth, ready } = useAuth();
  if (!ready) return <div className="flex h-screen items-center justify-center"><Spinner lg /></div>;
  return isAuth ? <Outlet /> : <Navigate to="/login" replace />;
}
```

---

## src/routes/DoctorRoute.jsx

```jsx
import { Navigate, Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../hooks/useDoctorAuth';
import Spinner from '../components/ui/Spinner';

export default function DoctorRoute() {
  const { isAuth, ready } = useDoctorAuth();
  if (!ready) return <div className="flex h-screen items-center justify-center"><Spinner lg /></div>;
  return isAuth ? <Outlet /> : <Navigate to="/doctor/login" replace />;
}
```

---

## src/components/ui/Spinner.jsx

```jsx
export default function Spinner({ lg }) {
  const s = lg ? 'h-10 w-10 border-[3px]' : 'h-5 w-5 border-2';
  return <div className={`${s} animate-spin rounded-full border-teal-500 border-t-transparent`} />;
}
```

---

## src/components/ui/Button.jsx

```jsx
import { clsx } from 'clsx';
import Spinner from './Spinner';

const variants = {
  primary:   'bg-teal-500 hover:bg-teal-400 text-navy-950 font-semibold shadow-lg shadow-teal-500/20',
  secondary: 'bg-white/10 hover:bg-white/15 text-slate-200 border border-white/20',
  danger:    'bg-risk-critical/20 hover:bg-risk-critical/30 text-risk-critical border border-risk-critical/30',
  ghost:     'text-slate-400 hover:text-slate-200 hover:bg-white/5',
  outline:   'border border-teal-500/50 text-teal-400 hover:bg-teal-500/10',
};

export default function Button({
  children, variant = 'primary', loading, disabled,
  className, type = 'button', size = 'md', ...rest
}) {
  const sz = size === 'sm' ? 'px-3 py-1.5 text-xs' : size === 'lg' ? 'px-6 py-3 text-base' : 'px-4 py-2 text-sm';
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl transition-all duration-200',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        variants[variant], sz, className
      )}
      {...rest}
    >
      {loading && <Spinner />}
      {children}
    </button>
  );
}
```

---

## src/components/ui/Input.jsx

```jsx
import { forwardRef } from 'react';
import { clsx } from 'clsx';

const Input = forwardRef(({ label, error, hint, className, type = 'text', ...rest }, ref) => (
  <div className="mb-4">
    {label && (
      <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">
        {label}
      </label>
    )}
    {type === 'textarea' ? (
      <textarea
        ref={ref}
        rows={3}
        className={clsx(
          'w-full px-4 py-2.5 rounded-xl bg-navy-800 border text-slate-100 text-sm',
          'placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-teal-500/50 resize-none',
          error ? 'border-risk-critical/60' : 'border-white/10 focus:border-teal-500/50',
          className
        )}
        {...rest}
      />
    ) : (
      <input
        ref={ref}
        type={type}
        className={clsx(
          'w-full px-4 py-2.5 rounded-xl bg-navy-800 border text-slate-100 text-sm',
          'placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-teal-500/50',
          error ? 'border-risk-critical/60' : 'border-white/10 focus:border-teal-500/50',
          className
        )}
        {...rest}
      />
    )}
    {error && <p className="mt-1 text-xs text-risk-critical">{error}</p>}
    {hint && !error && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
  </div>
));
Input.displayName = 'Input';
export default Input;
```

---

## src/components/ui/RiskBadge.jsx

```jsx
import { clsx } from 'clsx';

const cfg = {
  CRITICAL: { cls: 'risk-critical', dot: 'bg-risk-critical animate-pulse', label: 'CRITICAL' },
  HIGH:     { cls: 'risk-high',     dot: 'bg-risk-high',                   label: 'HIGH' },
  MEDIUM:   { cls: 'risk-medium',   dot: 'bg-risk-medium',                 label: 'MEDIUM' },
  LOW:      { cls: 'risk-low',      dot: 'bg-risk-low',                    label: 'LOW' },
};

export default function RiskBadge({ level, large }) {
  const c = cfg[level] || { cls: 'text-slate-400 bg-white/10 border-white/20', dot: 'bg-slate-500', label: level || '—' };
  return (
    <span className={clsx(
      'inline-flex items-center gap-1.5 rounded-full border font-mono font-semibold uppercase tracking-wide',
      large ? 'px-4 py-1.5 text-sm' : 'px-2.5 py-0.5 text-xs',
      c.cls
    )}>
      <span className={clsx('rounded-full', large ? 'h-2.5 w-2.5' : 'h-1.5 w-1.5', c.dot)} />
      {c.label}
    </span>
  );
}
```

---

## src/components/ui/StatCard.jsx

```jsx
export default function StatCard({ label, value, sub, icon: Icon, accent = 'teal' }) {
  const colors = {
    teal:     'text-teal-400   bg-teal-400/10   border-teal-400/20',
    critical: 'text-risk-critical bg-risk-critical/10 border-risk-critical/20',
    high:     'text-risk-high  bg-risk-high/10  border-risk-high/20',
    low:      'text-risk-low   bg-risk-low/10   border-risk-low/20',
    slate:    'text-slate-300  bg-white/5       border-white/10',
  };
  return (
    <div className="glass-card p-5 flex items-start gap-4 animate-fade-in">
      {Icon && (
        <div className={`p-2.5 rounded-xl border ${colors[accent]}`}>
          <Icon size={20} className={colors[accent].split(' ')[0]} />
        </div>
      )}
      <div>
        <p className="section-label">{label}</p>
        <p className="text-3xl font-display font-bold text-slate-100">{value ?? '—'}</p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
```

---

## src/components/ui/EmptyState.jsx

```jsx
export default function EmptyState({ icon, title, sub, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="text-5xl mb-4 opacity-30">{icon}</div>
      <p className="font-display text-lg font-semibold text-slate-300">{title}</p>
      {sub && <p className="text-sm text-slate-500 mt-1">{sub}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
```

---

## src/components/ui/Toast.jsx

```jsx
import { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

export default function Toast({ message, type = 'success', onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up">
      <div className={`flex items-center gap-3 px-4 py-3 rounded-2xl border shadow-2xl backdrop-blur
        ${type === 'success' ? 'bg-teal-500/20 border-teal-500/40 text-teal-200'
        : 'bg-risk-critical/20 border-risk-critical/40 text-red-200'}`}>
        {type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
        <span className="text-sm font-medium">{message}</span>
        <button onClick={onClose} className="ml-2 opacity-60 hover:opacity-100"><X size={14} /></button>
      </div>
    </div>
  );
}
```

---

## src/components/ui/Modal.jsx

```jsx
import { X } from 'lucide-react';
import { useEffect } from 'react';

export default function Modal({ open, onClose, title, children, wide }) {
  useEffect(() => {
    const handler = e => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative glass-card p-6 w-full animate-slide-up ${wide ? 'max-w-2xl' : 'max-w-lg'}`}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-display text-lg font-semibold text-slate-100">{title}</h3>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/10">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
```

---

## src/components/charts/RiskDonutChart.jsx

```jsx
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e' };

export default function RiskDonutChart({ data }) {
  // data: [{ name: 'CRITICAL', value: 3 }, ...]
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
          paddingAngle={3} dataKey="value" stroke="none">
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] || '#64748b'} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#0f2044', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}
          itemStyle={{ color: '#cbd5e1' }}
        />
        <Legend
          iconType="circle" iconSize={8}
          formatter={v => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

---

## src/components/visits/StepWizard.jsx

```jsx
import { CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';

export default function StepWizard({ steps, current }) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((label, i) => {
        const done   = i < current;
        const active = i === current;
        return (
          <div key={i} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div className={clsx(
                'h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-300',
                done   ? 'bg-teal-500 border-teal-500 text-navy-950'
                : active ? 'bg-transparent border-teal-400 text-teal-400 shadow-lg shadow-teal-500/30'
                :          'bg-transparent border-white/20 text-slate-500'
              )}>
                {done ? <CheckCircle size={14} /> : i + 1}
              </div>
              <span className={clsx(
                'text-xs mt-1.5 text-center font-medium whitespace-nowrap',
                active ? 'text-teal-400' : done ? 'text-slate-400' : 'text-slate-600'
              )}>
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={clsx(
                'flex-1 h-0.5 mx-2 mb-5 transition-colors duration-300',
                done ? 'bg-teal-500' : 'bg-white/10'
              )} />
            )}
          </div>
        );
      })}
    </div>
  );
}
```

---

## src/components/visits/ConfidenceBar.jsx

```jsx
export default function ConfidenceBar({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 70 ? 'bg-teal-500' : pct >= 50 ? 'bg-risk-medium' : 'bg-risk-high';
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span className="font-mono uppercase tracking-wider">AI Confidence</span>
        <span className="font-mono font-semibold text-slate-200">{pct}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-1000 ${color}`}
          style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
```

---

## src/components/visits/RiskReport.jsx

```jsx
import RiskBadge from '../ui/RiskBadge';
import ConfidenceBar from './ConfidenceBar';
import { AlertTriangle, Stethoscope, Brain, ClipboardList } from 'lucide-react';

export default function RiskReport({ risk }) {
  if (!risk) return null;
  const bannerColor = {
    CRITICAL: 'from-risk-critical/20 to-transparent border-risk-critical/40',
    HIGH:     'from-risk-high/20 to-transparent border-risk-high/40',
    MEDIUM:   'from-risk-medium/20 to-transparent border-risk-medium/40',
    LOW:      'from-risk-low/20 to-transparent border-risk-low/40',
  }[risk.riskLevel] || 'from-white/5 to-transparent border-white/10';

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Risk level banner */}
      <div className={`p-5 rounded-2xl border bg-gradient-to-br ${bannerColor}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {risk.isHighRisk && <AlertTriangle size={22} className="text-risk-critical" />}
            <span className="font-display text-xl font-bold text-slate-100">Risk Assessment</span>
          </div>
          <RiskBadge level={risk.riskLevel} large />
        </div>
        <ConfidenceBar value={risk.confidence} />
      </div>

      {/* Detected risks */}
      {risk.detectedRisks?.length > 0 && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 section-label mb-3">
            <AlertTriangle size={14} /> Detected Risk Factors ({risk.detectedRisks.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {risk.detectedRisks.map((r, i) => (
              <span key={i} className="text-xs px-3 py-1 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20 font-medium">
                {r}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      {risk.explanation && (
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 section-label mb-3">
            <Brain size={14} /> Clinical Explanation
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">{risk.explanation}</p>
        </div>
      )}

      {/* Recommendation */}
      {risk.recommendation && (
        <div className="glass-card p-5 border-teal-500/30">
          <div className="flex items-center gap-2 section-label mb-2 text-teal-400">
            <ClipboardList size={14} /> Recommendation
          </div>
          <p className="text-sm text-teal-200 font-medium leading-relaxed">{risk.recommendation}</p>
        </div>
      )}

      {/* Meta */}
      <div className="grid grid-cols-2 gap-3">
        {risk.age && (
          <div className="glass-card p-4">
            <p className="section-label">Patient Age</p>
            <p className="text-2xl font-display font-bold text-slate-100">{risk.age} <span className="text-sm font-sans font-normal text-slate-400">yrs</span></p>
          </div>
        )}
        {risk.gestationalWeeks && (
          <div className="glass-card p-4">
            <p className="section-label">Gestational Age</p>
            <p className="text-2xl font-display font-bold text-slate-100">{risk.gestationalWeeks} <span className="text-sm font-sans font-normal text-slate-400">wks</span></p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## src/components/video/VideoRoom.jsx

```jsx
import { useEffect, useRef } from 'react';
import { PhoneOff } from 'lucide-react';

export default function VideoRoom({ roomUrl, token, onLeave }) {
  const containerRef = useRef(null);
  const callRef      = useRef(null);

  useEffect(() => {
    if (!roomUrl || !containerRef.current) return;

    let destroyed = false;
    (async () => {
      const DailyIframe = (await import('@daily-co/daily-js')).default;
      if (destroyed) return;
      if (callRef.current) await callRef.current.destroy();

      callRef.current = DailyIframe.createFrame(containerRef.current, {
        iframeStyle: { width: '100%', height: '100%', border: 'none', borderRadius: '16px' },
        showLeaveButton: true,
        showFullscreenButton: true,
        theme: {
          colors: {
            accent: '#14b8a6', accentText: '#050d1a',
            background: '#0a1628', backgroundAccent: '#0f2044',
            baseText: '#e2e8f0', border: '#1a3560',
          }
        }
      });
      callRef.current.on('left-meeting', () => { if (onLeave) onLeave(); });
      await callRef.current.join({ url: roomUrl, token });
    })();

    return () => {
      destroyed = true;
      if (callRef.current) { callRef.current.destroy(); callRef.current = null; }
    };
  }, [roomUrl, token]);

  return (
    <div className="rounded-2xl overflow-hidden border border-white/10 relative" style={{ height: 480 }}>
      <div ref={containerRef} className="w-full h-full bg-navy-900" />
      {onLeave && (
        <button
          onClick={onLeave}
          className="absolute bottom-4 right-4 flex items-center gap-2 px-4 py-2 rounded-xl bg-risk-critical/80 hover:bg-risk-critical text-white text-sm font-medium transition-colors"
        >
          <PhoneOff size={16} /> Leave Call
        </button>
      )}
    </div>
  );
}
```

---

## src/components/layout/WorkerLayout.jsx

```jsx
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { LayoutDashboard, Users, UserPlus, AlertTriangle, LogOut, Activity } from 'lucide-react';

const nav = [
  { to: '/dashboard',    icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/patients',     icon: Users,           label: 'Patients' },
  { to: '/patients/new', icon: UserPlus,        label: 'New Patient' },
];

export default function WorkerLayout() {
  const { user, logout } = useAuth();
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-navy-900 border-r border-white/10 flex flex-col">
        {/* Logo */}
        <div className="px-6 pt-6 pb-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-teal-500 flex items-center justify-center">
              <Activity size={16} className="text-navy-950" />
            </div>
            <div>
              <p className="font-display text-sm font-bold text-slate-100 leading-none">ANC Portal</p>
              <p className="text-[10px] font-mono text-teal-400 uppercase tracking-widest mt-0.5">Worker</p>
            </div>
          </div>
        </div>

        {/* User card */}
        {user && (
          <div className="mx-3 mt-3 p-3 rounded-xl bg-white/5 border border-white/10">
            <p className="text-xs font-semibold text-slate-200 truncate">{user.fullName}</p>
            <p className="text-[11px] text-teal-400 truncate mt-0.5">{user.healthCenter}</p>
            <p className="text-[10px] text-slate-500 truncate">{user.district}</p>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150
               ${isActive
                ? 'bg-teal-500/15 text-teal-300 border border-teal-500/25 font-medium'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`
            }>
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-3 pb-4">
          <button onClick={logout}
            className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-500 hover:text-risk-critical hover:bg-risk-critical/10 transition-all">
            <LogOut size={17} /> Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto bg-navy-950">
        <Outlet />
      </main>
    </div>
  );
}
```

---

## src/components/layout/DoctorLayout.jsx

```jsx
import { NavLink, Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import { LayoutDashboard, ListOrdered, Clock, LogOut, Stethoscope } from 'lucide-react';

const nav = [
  { to: '/doctor/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/doctor/queue',     icon: ListOrdered,     label: 'Patient Queue' },
  { to: '/doctor/history',   icon: Clock,           label: 'History' },
];

export default function DoctorLayout() {
  const { doctor, logout } = useDoctorAuth();
  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-60 flex-shrink-0 bg-navy-900 border-r border-white/10 flex flex-col">
        <div className="px-6 pt-6 pb-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-indigo-500 flex items-center justify-center">
              <Stethoscope size={16} className="text-white" />
            </div>
            <div>
              <p className="font-display text-sm font-bold text-slate-100 leading-none">ANC Portal</p>
              <p className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest mt-0.5">Doctor</p>
            </div>
          </div>
        </div>

        {doctor && (
          <div className="mx-3 mt-3 p-3 rounded-xl bg-white/5 border border-white/10">
            <p className="text-xs font-semibold text-slate-200 truncate">Dr. {doctor.fullName}</p>
            <p className="text-[11px] text-indigo-400 truncate mt-0.5">{doctor.specialization}</p>
            <p className="text-[10px] text-slate-500 truncate">{doctor.hospital}</p>
          </div>
        )}

        <nav className="flex-1 px-3 py-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150
               ${isActive
                ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/25 font-medium'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'}`
            }>
              <Icon size={17} /> {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 pb-4">
          <button onClick={logout}
            className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-500 hover:text-risk-critical hover:bg-risk-critical/10 transition-all">
            <LogOut size={17} /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto bg-navy-950"><Outlet /></main>
    </div>
  );
}
```

---

## src/pages/worker/LoginPage.jsx

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Activity, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const { login }  = useAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async ({ phone, password }) => {
    setErr('');
    try { await login(phone, password); navigate('/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Login failed. Check your credentials.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex">
      {/* Left panel */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-navy-900 via-navy-800 to-teal-900/30 flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-teal-500 flex items-center justify-center">
            <Activity size={20} className="text-navy-950" />
          </div>
          <span className="font-display text-xl font-bold text-slate-100">ANC Portal</span>
        </div>
        <div>
          <blockquote className="text-3xl font-display font-bold text-slate-100 leading-snug mb-4">
            Maternal health<br />intelligence at<br />every level of care.
          </blockquote>
          <p className="text-slate-400 text-sm">
            AI-powered risk assessment for Antenatal Care workers —<br />connecting field workers with specialists in real-time.
          </p>
        </div>
        <div className="flex gap-6 text-xs font-mono text-slate-500">
          <span>CRITICAL ALERTS</span>
          <span>REAL-TIME TRIAGE</span>
          <span>VIDEO CONSULT</span>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm animate-fade-in">
          <div className="mb-8">
            <p className="section-label">ANC Worker Portal</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Sign in</h1>
            <p className="text-slate-400 text-sm mt-1">Enter your phone number and password</p>
          </div>

          {err && (
            <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
              <AlertCircle size={16} className="flex-shrink-0" /> {err}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              label="Phone Number"
              type="tel"
              placeholder="9876543210"
              error={errors.phone?.message}
              {...register('phone', {
                required: 'Phone number is required',
                pattern: { value: /^[6-9]\d{9}$/, message: 'Enter a valid 10-digit mobile number' },
              })}
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register('password', { required: 'Password is required' })}
            />
            <Button type="submit" loading={isSubmitting} className="w-full mt-2" size="lg">
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            New worker?{' '}
            <Link to="/signup" className="text-teal-400 hover:text-teal-300 font-medium">
              Create account
            </Link>
          </p>
          <p className="text-center text-xs text-slate-600 mt-3">
            Doctor?{' '}
            <Link to="/doctor/login" className="text-slate-400 hover:text-slate-300">
              Doctor portal →
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/SignupPage.jsx

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Activity, AlertCircle } from 'lucide-react';

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    setErr('');
    try { await signup(data); navigate('/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Signup failed. Please try again.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-fade-in">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="h-10 w-10 rounded-xl bg-teal-500 flex items-center justify-center">
            <Activity size={20} className="text-navy-950" />
          </div>
          <div>
            <p className="section-label">Worker Registration</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Create account</h1>
          </div>
        </div>

        {err && (
          <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
            <AlertCircle size={16} className="flex-shrink-0" /> {err}
          </div>
        )}

        <div className="glass-card p-6">
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="grid grid-cols-2 gap-x-4">
              <div className="col-span-2">
                <Input label="Full Name *" placeholder="Anjali Devi"
                  error={errors.fullName?.message}
                  {...register('fullName', { required: 'Full name is required' })} />
              </div>
              <Input label="Phone *" type="tel" placeholder="9876543210"
                error={errors.phone?.message}
                {...register('phone', {
                  required: 'Phone is required',
                  pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid number' },
                })} />
              <Input label="Email" type="email" placeholder="anjali@phc.in"
                {...register('email')} />
              <div className="col-span-2">
                <Input label="Password *" type="password" placeholder="Min. 8 characters"
                  error={errors.password?.message}
                  {...register('password', { required: true, minLength: { value: 8, message: 'Min 8 chars' } })} />
              </div>
              <Input label="Health Center *" placeholder="PHC Angondhalli"
                error={errors.healthCenter?.message}
                {...register('healthCenter', { required: 'Health center is required' })} />
              <Input label="District *" placeholder="Bangalore Rural"
                error={errors.district?.message}
                {...register('district', { required: 'District is required' })} />
            </div>
            <Button type="submit" loading={isSubmitting} className="w-full mt-2" size="lg">
              Create Account
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-slate-500 mt-5">
          Already registered?{' '}
          <Link to="/login" className="text-teal-400 hover:text-teal-300 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/DashboardPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { getPatients } from '../../api/patientApi';
import { getHighRisk, getCritical } from '../../api/visitApi';
import StatCard from '../../components/ui/StatCard';
import RiskBadge from '../../components/ui/RiskBadge';
import RiskDonutChart from '../../components/charts/RiskDonutChart';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import { Users, AlertTriangle, Activity, TrendingUp, ChevronRight, Plus } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const { user }    = useAuth();
  const navigate    = useNavigate();
  const [data,  setData]  = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getPatients(), getHighRisk(), getCritical()])
      .then(([patients, highRisk, critical]) => {
        const high   = highRisk.filter(v => v.riskLevel === 'HIGH');
        const medium = highRisk.filter(v => v.riskLevel === 'MEDIUM');
        setData({ patients, highRisk, critical, high, medium });
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex h-full items-center justify-center">
      <Spinner lg />
    </div>
  );

  const chartData = [
    { name: 'CRITICAL', value: data.critical.length },
    { name: 'HIGH',     value: data.high.length },
    { name: 'MEDIUM',   value: data.medium.length },
  ].filter(d => d.value > 0);

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="section-label">Overview</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">
            Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {user?.fullName?.split(' ')[0]}
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">{user?.healthCenter} · {user?.district}</p>
        </div>
        <Button onClick={() => navigate('/patients/new')} className="gap-2">
          <Plus size={16} /> New Patient
        </Button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Patients"  value={data.patients.length}  icon={Users}          accent="slate" />
        <StatCard label="High Risk"       value={data.highRisk.length}  icon={TrendingUp}     accent="high" />
        <StatCard label="Critical"        value={data.critical.length}  icon={AlertTriangle}  accent="critical" />
        <StatCard label="All Visits"      value={data.highRisk.length}  icon={Activity}       accent="teal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* CRITICAL alerts */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <p className="section-label flex items-center gap-1.5">
              <AlertTriangle size={12} /> Critical Cases
            </p>
            <span className="text-xs text-slate-500">{data.critical.length} total</span>
          </div>
          <div className="space-y-2">
            {data.critical.length === 0 ? (
              <div className="glass-card p-8 text-center text-slate-500 text-sm">
                ✓ No critical cases at this time
              </div>
            ) : data.critical.slice(0, 5).map(v => (
              <button
                key={v.id}
                onClick={() => navigate(`/visits/${v.id}`)}
                className="w-full glass-card p-4 flex items-center justify-between hover:border-risk-critical/40 transition-colors group"
              >
                <div className="flex items-center gap-3 text-left">
                  <div className="h-2 w-2 rounded-full bg-risk-critical animate-pulse flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-slate-200">{v.patientName || `Patient #${v.patientId?.slice(-6)}`}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {v.detectedRisks?.slice(0,2).join(' · ')}
                      {v.createdAt && ` · ${formatDistanceToNow(new Date(v.createdAt), { addSuffix: true })}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <RiskBadge level={v.riskLevel} />
                  <ChevronRight size={16} className="text-slate-600 group-hover:text-slate-300 transition-colors" />
                </div>
              </button>
            ))}
          </div>
          {data.critical.length > 5 && (
            <button onClick={() => navigate('/patients')}
              className="mt-2 w-full text-xs text-slate-500 hover:text-teal-400 py-2 transition-colors">
              View all {data.critical.length} critical cases →
            </button>
          )}
        </div>

        {/* Risk chart + quick actions */}
        <div className="space-y-4">
          {chartData.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-2">Risk Distribution</p>
              <RiskDonutChart data={chartData} />
            </div>
          )}
          <div className="glass-card p-4 space-y-2">
            <p className="section-label">Quick Actions</p>
            <Button variant="outline" className="w-full justify-start gap-2" onClick={() => navigate('/patients/new')}>
              <Plus size={15} /> Register Patient
            </Button>
            <Button variant="secondary" className="w-full justify-start gap-2" onClick={() => navigate('/patients')}>
              <Users size={15} /> View All Patients
            </Button>
          </div>

          {/* Recent patients */}
          {data.patients.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-3">Recent Patients</p>
              <div className="space-y-2">
                {data.patients.slice(0, 4).map(p => (
                  <button key={p.patientId}
                    onClick={() => navigate(`/patients/${p.patientId}`)}
                    className="w-full flex items-center justify-between hover:bg-white/5 rounded-lg p-1.5 -mx-1.5 transition-colors group">
                    <span className="text-sm text-slate-300 truncate">{p.fullName}</span>
                    <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400 flex-shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/PatientListPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPatients } from '../../api/patientApi';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import EmptyState from '../../components/ui/EmptyState';
import { Plus, Search, ChevronRight, MapPin, Phone, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function PatientListPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [query,    setQuery]    = useState('');

  useEffect(() => {
    getPatients().then(d => { setPatients(d); setFiltered(d); }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const q = query.toLowerCase();
    setFiltered(patients.filter(p =>
      p.fullName?.toLowerCase().includes(q) ||
      p.phone?.includes(q) ||
      p.village?.toLowerCase().includes(q)
    ));
  }, [query, patients]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="section-label">Registry</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Patients</h1>
          <p className="text-slate-400 text-sm">{patients.length} registered</p>
        </div>
        <Button onClick={() => navigate('/patients/new')}>
          <Plus size={16} /> New Patient
        </Button>
      </div>

      {/* Search */}
      <div className="relative mb-5">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search by name, phone, village..."
          className="w-full pl-10 pr-4 py-2.5 bg-navy-800 border border-white/10 rounded-xl text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-teal-500/50"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon="🤱"
          title={query ? 'No patients match your search' : 'No patients registered yet'}
          sub={query ? 'Try a different search term' : 'Click "New Patient" to register your first patient'}
          action={!query && <Button onClick={() => navigate('/patients/new')}><Plus size={16} /> Register Patient</Button>}
        />
      ) : (
        <div className="space-y-2">
          {filtered.map(p => (
            <button
              key={p.patientId}
              onClick={() => navigate(`/patients/${p.patientId}`)}
              className="w-full glass-card p-4 flex items-center justify-between hover:border-teal-500/30 transition-all group text-left"
            >
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-teal-500/20 border border-teal-500/30 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-teal-300">{p.fullName?.[0]?.toUpperCase()}</span>
                </div>
                <div>
                  <p className="font-medium text-slate-100">{p.fullName}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    {p.phone && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <Phone size={10} /> {p.phone}
                      </span>
                    )}
                    {p.village && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <MapPin size={10} /> {p.village}
                      </span>
                    )}
                    {p.age && (
                      <span className="text-xs text-slate-500">Age {p.age}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {p.lmpDate && (
                  <span className="flex items-center gap-1 text-xs text-slate-500">
                    <Calendar size={10} /> {format(new Date(p.lmpDate), 'dd MMM yyyy')}
                  </span>
                )}
                <ChevronRight size={16} className="text-slate-600 group-hover:text-teal-400 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## src/pages/worker/PatientCreatePage.jsx

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { createPatient } from '../../api/patientApi';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { AlertCircle, UserPlus } from 'lucide-react';

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function PatientCreatePage() {
  const navigate = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    setErr('');
    try {
      const patient = await createPatient({
        ...data,
        age: data.age ? Number(data.age) : null,
      });
      navigate(`/patients/${patient.patientId}`);
    } catch (e) {
      setErr(e.response?.data?.message || 'Failed to register patient');
    }
  };

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      <div className="mb-6">
        <p className="section-label">Registration</p>
        <h1 className="font-display text-2xl font-bold text-slate-100 flex items-center gap-2">
          <UserPlus size={24} className="text-teal-400" /> New Patient
        </h1>
      </div>

      {err && (
        <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
          <AlertCircle size={16} /> {err}
        </div>
      )}

      <div className="glass-card p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          {/* Personal info */}
          <p className="section-label mb-3">Personal Information</p>
          <div className="grid grid-cols-2 gap-x-4">
            <div className="col-span-2">
              <Input label="Full Name *" placeholder="Meena Kumari"
                error={errors.fullName?.message}
                {...register('fullName', { required: 'Full name is required' })} />
            </div>
            <Input label="Phone" type="tel" placeholder="9123456789" {...register('phone')} />
            <Input label="Age" type="number" placeholder="24"
              {...register('age', { min: { value: 10, message: 'Invalid age' }, max: { value: 60, message: 'Invalid age' } })}
              error={errors.age?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-x-4">
            <div className="mb-4">
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">Blood Group</label>
              <select className="w-full px-4 py-2.5 rounded-xl bg-navy-800 border border-white/10 text-slate-100 text-sm focus:outline-none focus:border-teal-500/50"
                {...register('bloodGroup')}>
                <option value="">— Select —</option>
                {BLOOD_GROUPS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <Input label="Village" placeholder="Hebbal" {...register('village')} />
          </div>

          <div className="grid grid-cols-2 gap-x-4">
            <Input label="District" placeholder="Bangalore Rural" {...register('district')} />
            <Input label="Address" placeholder="123 Main St" {...register('address')} />
          </div>

          {/* Pregnancy info */}
          <p className="section-label mb-3 mt-2">Pregnancy Details</p>
          <div className="grid grid-cols-2 gap-x-4">
            <Input label="LMP Date" type="date"
              hint="Last Menstrual Period"
              {...register('lmpDate')} />
            <Input label="EDD Date" type="date"
              hint="Expected Due Date"
              {...register('eddDate')} />
          </div>

          <div className="flex gap-3 mt-4 pt-4 border-t border-white/10">
            <Button type="submit" loading={isSubmitting} size="lg">
              Register Patient
            </Button>
            <Button variant="secondary" onClick={() => navigate('/patients')} size="lg">
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/PatientDetailPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPatient } from '../../api/patientApi';
import { getPatientVisits } from '../../api/visitApi';
import { getPatientConsults } from '../../api/consultationApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Button from '../../components/ui/Button';
import Spinner from '../../components/ui/Spinner';
import { Plus, Phone, MapPin, Droplets, Calendar, ChevronRight, Video, Stethoscope } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

function InfoPill({ icon: Icon, label, value }) {
  if (!value) return null;
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon size={14} className="text-slate-500 flex-shrink-0" />
      <span className="text-slate-400 text-xs">{label}:</span>
      <span className="text-slate-200 font-medium">{value}</span>
    </div>
  );
}

export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient,   setPatient]   = useState(null);
  const [visits,    setVisits]    = useState([]);
  const [consults,  setConsults]  = useState([]);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([getPatient(id), getPatientVisits(id), getPatientConsults(id)])
      .then(([p, v, c]) => { setPatient(p); setVisits(v); setConsults(c); })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!patient) return <div className="p-8 text-slate-400">Patient not found.</div>;

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="section-label">Patient Profile</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">{patient.fullName}</h1>
          <div className="flex flex-wrap gap-4 mt-2">
            <InfoPill icon={Phone}   label="Phone"  value={patient.phone} />
            <InfoPill icon={MapPin}  label="Village" value={[patient.village, patient.district].filter(Boolean).join(', ')} />
            <InfoPill icon={Droplets} label="Blood Group" value={patient.bloodGroup} />
            <InfoPill icon={Calendar} label="LMP" value={patient.lmpDate && format(new Date(patient.lmpDate), 'dd MMM yyyy')} />
            <InfoPill icon={Calendar} label="EDD" value={patient.eddDate && format(new Date(patient.eddDate), 'dd MMM yyyy')} />
          </div>
        </div>
        <Button onClick={() => navigate(`/visits/new/${patient.patientId}`)}>
          <Plus size={16} /> New Visit
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Visit history */}
        <div className="lg:col-span-2">
          <p className="section-label mb-3">Visit History ({visits.length})</p>
          {visits.length === 0 ? (
            <div className="glass-card p-10 text-center">
              <p className="text-slate-500 text-sm mb-3">No visits recorded yet</p>
              <Button onClick={() => navigate(`/visits/new/${patient.patientId}`)} variant="outline">
                <Plus size={16} /> Record First Visit
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {visits.map(v => (
                <button
                  key={v.id}
                  onClick={() => navigate(`/visits/${v.id}`)}
                  className="w-full glass-card p-4 flex items-center justify-between hover:border-teal-500/30 transition-all group text-left"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <RiskBadge level={v.riskLevel} />
                      <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                        ${v.status === 'AI_ANALYZED' ? 'text-teal-400 bg-teal-400/10'
                        : v.status === 'AI_FAILED'   ? 'text-risk-high bg-risk-high/10'
                        : 'text-slate-400 bg-white/5'}`}>
                        {v.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">
                      {v.createdAt && format(new Date(v.createdAt), 'dd MMM yyyy, HH:mm')}
                      {v.confidence && ` · Confidence ${Math.round(v.confidence * 100)}%`}
                    </p>
                    {v.detectedRisks?.length > 0 && (
                      <p className="text-xs text-slate-600 mt-1 truncate max-w-md">
                        {v.detectedRisks.slice(0, 3).join(' · ')}
                      </p>
                    )}
                  </div>
                  <ChevronRight size={16} className="text-slate-600 group-hover:text-teal-400 transition-colors flex-shrink-0" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Consultations */}
        <div>
          <p className="section-label mb-3">Doctor Consultations ({consults.length})</p>
          {consults.length === 0 ? (
            <div className="glass-card p-6 text-center">
              <Stethoscope size={24} className="text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500 text-xs">No consultations yet</p>
              <p className="text-slate-600 text-xs mt-1">Consultations are auto-created when a visit is flagged as high risk</p>
            </div>
          ) : (
            <div className="space-y-2">
              {consults.map(c => (
                <div key={c.consultationId} className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <RiskBadge level={c.riskLevel} />
                    <span className={`text-xs font-mono px-2 py-0.5 rounded-full
                      ${c.status === 'COMPLETED'   ? 'text-teal-400 bg-teal-400/10'
                      : c.status === 'IN_PROGRESS' ? 'text-risk-medium bg-risk-medium/10 animate-pulse'
                      : c.status === 'ACCEPTED'    ? 'text-indigo-400 bg-indigo-400/10'
                      : 'text-slate-400 bg-white/5'}`}>
                      {c.status}
                    </span>
                  </div>
                  {c.doctorName && (
                    <p className="text-xs text-slate-400">Dr. {c.doctorName}</p>
                  )}
                  {c.status === 'IN_PROGRESS' && c.workerToken && c.roomUrl && (
                    <a
                      href={`${c.roomUrl}?t=${c.workerToken}`}
                      target="_blank" rel="noreferrer"
                      className="mt-2 flex items-center justify-center gap-1.5 w-full text-xs py-2 rounded-lg bg-teal-500/20 text-teal-300 border border-teal-500/30 hover:bg-teal-500/30 transition-colors"
                    >
                      <Video size={12} /> Join Video Call
                    </a>
                  )}
                  {c.status === 'COMPLETED' && c.actionPlan && (
                    <div className="mt-2 p-2 rounded-lg bg-white/5 text-xs text-slate-300">
                      <p className="font-mono text-teal-400 mb-1">Action Plan:</p>
                      <p className="leading-relaxed">{c.actionPlan}</p>
                    </div>
                  )}
                  <p className="text-[10px] text-slate-600 mt-2">
                    {c.createdAt && formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/VisitFormPage.jsx

```jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { registerVisit } from '../../api/visitApi';
import StepWizard from '../../components/visits/StepWizard';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { AlertCircle, ChevronLeft, ChevronRight, Zap } from 'lucide-react';

const STEPS = ['Patient Info', 'Vitals', 'Lab Reports', 'Medical History', 'Obstetric History', 'Pregnancy', 'Symptoms'];

function CheckRow({ label, name, register }) {
  return (
    <label className="flex items-center gap-3 p-3 rounded-xl border border-white/10 hover:border-teal-500/30 hover:bg-teal-500/5 cursor-pointer transition-all group">
      <input type="checkbox" className="h-4 w-4 rounded border-slate-600 bg-navy-800 text-teal-500 focus:ring-teal-500/30"
        {...register(name)} />
      <span className="text-sm text-slate-300 group-hover:text-slate-100">{label}</span>
    </label>
  );
}

export default function VisitFormPage() {
  const { patientId } = useParams();
  const navigate      = useNavigate();
  const [step, setStep]       = useState(0);
  const [saved, setSaved]     = useState({});
  const [err,   setErr]       = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const saveAndNext = (data) => {
    setSaved(prev => ({ ...prev, ...data }));
    if (step < 6) { setStep(s => s + 1); reset(); }
  };

  const submitAll = async (data) => {
    setErr(''); setSubmitting(true);
    const all = { ...saved, ...data };

    const payload = {
      patientId,
      structured_data: {
        patient_info:      { age: Number(all.age) || null, gestationalWeeks: Number(all.gestationalWeeks) || null },
        vitals:            { heightCm: Number(all.heightCm)||null, bmi: Number(all.bmi)||null, bpSystolic: Number(all.bpSystolic)||null, bpDiastolic: Number(all.bpDiastolic)||null },
        lab_reports:       { hemoglobin: Number(all.hemoglobin)||null, rhNegative: !!all.rhNegative, hivPositive: !!all.hivPositive, syphilisPositive: !!all.syphilisPositive, urineProtein: !!all.urineProtein, urineSugar: !!all.urineSugar },
        medical_history:   { previousLSCS: !!all.previousLSCS, badObstetricHistory: !!all.badObstetricHistory, previousStillbirth: !!all.previousStillbirth, previousPretermDelivery: !!all.previousPretermDelivery, previousAbortion: !!all.previousAbortion, chronicHypertension: !!all.chronicHypertension, diabetes: !!all.diabetes, thyroidDisorder: !!all.thyroidDisorder, smoking: !!all.smoking, tobaccoUse: !!all.tobaccoUse, alcoholUse: !!all.alcoholUse, systemicIllness: all.systemicIllness || 'None' },
        obstetric_history: { birthOrder: Number(all.birthOrder)||null, interPregnancyInterval: Number(all.interPregnancyInterval)||null, stillbirthCount: Number(all.stillbirthCount)||0, abortionCount: Number(all.abortionCount)||0, pretermHistory: !!all.pretermHistory },
        pregnancy_details: { twinPregnancy: !!all.twinPregnancy, malpresentation: !!all.malpresentation, placentaPrevia: !!all.placentaPrevia, reducedFetalMovement: !!all.reducedFetalMovement, amnioticFluidNormal: all.amnioticFluidNormal !== false, umbilicalDopplerAbnormal: !!all.umbilicalDopplerAbnormal },
        current_symptoms:  { headache: !!all.headache, visualDisturbance: !!all.visualDisturbance, epigastricPain: !!all.epigastricPain, decreasedUrineOutput: !!all.decreasedUrineOutput, bleedingPerVagina: !!all.bleedingPerVagina, convulsions: !!all.convulsions },
      }
    };

    try {
      const result = await registerVisit(payload);
      navigate(`/visits/${result.visitId}`, { state: result });
    } catch (e) {
      setErr(e.response?.data?.message || 'Failed to submit. Please try again.');
    } finally { setSubmitting(false); }
  };

  const onSubmit = step < 6 ? saveAndNext : submitAll;

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      <div className="mb-6">
        <p className="section-label">ANC Visit</p>
        <h1 className="font-display text-2xl font-bold text-slate-100">Register Visit</h1>
        <p className="text-xs text-slate-500 font-mono mt-0.5">Patient: {patientId?.slice(0,8)}...</p>
      </div>

      <StepWizard steps={STEPS} current={step} />

      {err && (
        <div className="flex items-center gap-2 mb-4 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
          <AlertCircle size={16} /> {err}
        </div>
      )}

      <div className="glass-card p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          {/* Step 0: Patient Info */}
          {step === 0 && (
            <div>
              <p className="section-label mb-4">Patient Information</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Age (years) *" type="number" placeholder="28"
                  error={errors.age?.message}
                  {...register('age', { required: 'Age is required', min: { value: 15, message: 'Min 15' }, max: { value: 55, message: 'Max 55' } })} />
                <Input label="Gestational Weeks *" type="number" placeholder="28"
                  error={errors.gestationalWeeks?.message}
                  {...register('gestationalWeeks', { required: 'Required', min: { value: 1, message: 'Min 1' }, max: { value: 42, message: 'Max 42' } })} />
              </div>
            </div>
          )}

          {/* Step 1: Vitals */}
          {step === 1 && (
            <div>
              <p className="section-label mb-4">Vitals</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Height (cm)" type="number" placeholder="155" {...register('heightCm')} />
                <Input label="BMI" type="number" placeholder="24.5" step="0.1" {...register('bmi')} />
                <Input label="BP Systolic (mmHg)" type="number" placeholder="120" {...register('bpSystolic')} />
                <Input label="BP Diastolic (mmHg)" type="number" placeholder="80"  {...register('bpDiastolic')} />
              </div>
            </div>
          )}

          {/* Step 2: Lab Reports */}
          {step === 2 && (
            <div>
              <p className="section-label mb-4">Lab Reports</p>
              <Input label="Hemoglobin (g/dL)" type="number" placeholder="11.5" step="0.1" {...register('hemoglobin')} />
              <p className="text-xs text-slate-500 mb-3">Mark all that apply:</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="Rh Negative"       name="rhNegative"       register={register} />
                <CheckRow label="HIV Positive"       name="hivPositive"      register={register} />
                <CheckRow label="Syphilis Positive"  name="syphilisPositive" register={register} />
                <CheckRow label="Urine Protein +"    name="urineProtein"     register={register} />
                <CheckRow label="Urine Sugar +"      name="urineSugar"       register={register} />
              </div>
            </div>
          )}

          {/* Step 3: Medical History */}
          {step === 3 && (
            <div>
              <p className="section-label mb-4">Medical History</p>
              <div className="grid grid-cols-1 gap-2 mb-4">
                <CheckRow label="Previous LSCS (C-Section)"       name="previousLSCS"           register={register} />
                <CheckRow label="Bad Obstetric History"            name="badObstetricHistory"     register={register} />
                <CheckRow label="Previous Stillbirth"              name="previousStillbirth"      register={register} />
                <CheckRow label="Previous Preterm Delivery"        name="previousPretermDelivery" register={register} />
                <CheckRow label="Previous Abortion"                name="previousAbortion"        register={register} />
                <CheckRow label="Chronic Hypertension"             name="chronicHypertension"     register={register} />
                <CheckRow label="Diabetes"                         name="diabetes"                register={register} />
                <CheckRow label="Thyroid Disorder"                 name="thyroidDisorder"         register={register} />
                <CheckRow label="Smoking"                          name="smoking"                 register={register} />
                <CheckRow label="Tobacco Use"                      name="tobaccoUse"              register={register} />
                <CheckRow label="Alcohol Use"                      name="alcoholUse"              register={register} />
              </div>
              <Input label="Systemic Illness (if any)" placeholder="e.g. Heart disease, or None" {...register('systemicIllness')} />
            </div>
          )}

          {/* Step 4: Obstetric History */}
          {step === 4 && (
            <div>
              <p className="section-label mb-4">Obstetric History</p>
              <div className="grid grid-cols-2 gap-x-4">
                <Input label="Birth Order (Gravida)" type="number" placeholder="2"  {...register('birthOrder')} />
                <Input label="Inter-Pregnancy Interval (months)" type="number" placeholder="24" {...register('interPregnancyInterval')} />
                <Input label="Stillbirth Count" type="number" placeholder="0" {...register('stillbirthCount')} />
                <Input label="Abortion Count"   type="number" placeholder="0" {...register('abortionCount')} />
              </div>
              <CheckRow label="Preterm History" name="pretermHistory" register={register} />
            </div>
          )}

          {/* Step 5: Pregnancy Details */}
          {step === 5 && (
            <div>
              <p className="section-label mb-4">Current Pregnancy Details</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="Twin / Multiple Pregnancy"       name="twinPregnancy"           register={register} />
                <CheckRow label="Malpresentation"                 name="malpresentation"         register={register} />
                <CheckRow label="Placenta Previa"                 name="placentaPrevia"          register={register} />
                <CheckRow label="Reduced Fetal Movements"         name="reducedFetalMovement"    register={register} />
                <CheckRow label="Abnormal Umbilical Doppler"      name="umbilicalDopplerAbnormal" register={register} />
                <label className="flex items-center gap-3 p-3 rounded-xl border border-white/10 hover:border-teal-500/30 cursor-pointer transition-all group">
                  <input type="checkbox" defaultChecked
                    className="h-4 w-4 rounded border-slate-600 bg-navy-800 text-teal-500"
                    {...register('amnioticFluidNormal')} />
                  <span className="text-sm text-slate-300">Amniotic Fluid Normal</span>
                </label>
              </div>
            </div>
          )}

          {/* Step 6: Symptoms */}
          {step === 6 && (
            <div>
              <p className="section-label mb-1">Current Symptoms</p>
              <p className="text-xs text-slate-500 mb-4">Mark all symptoms the patient is currently experiencing</p>
              <div className="grid grid-cols-1 gap-2">
                <CheckRow label="🤕 Headache"                name="headache"             register={register} />
                <CheckRow label="👁 Visual Disturbance"     name="visualDisturbance"    register={register} />
                <CheckRow label="🫁 Epigastric Pain"        name="epigastricPain"       register={register} />
                <CheckRow label="💧 Decreased Urine Output" name="decreasedUrineOutput" register={register} />
                <CheckRow label="🩸 Bleeding Per Vagina"    name="bleedingPerVagina"    register={register} />
                <CheckRow label="⚡ Convulsions"            name="convulsions"           register={register} />
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/10">
            {step > 0 ? (
              <Button variant="secondary" onClick={() => { setStep(s => s - 1); reset(); }}>
                <ChevronLeft size={16} /> Back
              </Button>
            ) : (
              <Button variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
            )}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-mono">{step + 1} / {STEPS.length}</span>
              <Button type="submit" loading={submitting && step === 6}>
                {step < 6 ? (<>Next <ChevronRight size={16} /></>) : (<><Zap size={16} /> Analyze Risk</>)}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## src/pages/worker/VisitResultPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { getVisit } from '../../api/visitApi';
import RiskReport from '../../components/visits/RiskReport';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import { ArrowLeft, Printer, Stethoscope } from 'lucide-react';
import { format } from 'date-fns';

export default function VisitResultPage() {
  const { visitId } = useParams();
  const { state }   = useLocation();
  const navigate    = useNavigate();
  const [visit, setVisit]   = useState(state || null);
  const [loading, setLoading] = useState(!state);

  useEffect(() => {
    if (!state) {
      getVisit(visitId).then(d => setVisit(d)).finally(() => setLoading(false));
    }
  }, [visitId, state]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!visit)  return <div className="p-8 text-slate-400">Visit not found.</div>;

  const risk = visit.riskAssessment;

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate(-1)}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-teal-400 mb-2 transition-colors">
            <ArrowLeft size={14} /> Back
          </button>
          <p className="section-label">Visit Result</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Risk Assessment</h1>
          <p className="text-xs text-slate-500 font-mono mt-0.5">
            {visit.savedAt && format(new Date(visit.savedAt), 'dd MMM yyyy, HH:mm')}
            {' · '}
            <span className={`${visit.status === 'AI_ANALYZED' ? 'text-teal-400' : visit.status === 'AI_FAILED' ? 'text-risk-high' : 'text-slate-400'}`}>
              {visit.status}
            </span>
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => window.print()}>
            <Printer size={15} />
          </Button>
          {visit.patientId && (
            <Button variant="secondary" size="sm" onClick={() => navigate(`/patients/${visit.patientId}`)}>
              <Stethoscope size={15} /> Patient
            </Button>
          )}
        </div>
      </div>

      {risk ? (
        <RiskReport risk={risk} />
      ) : (
        <div className="glass-card p-8 text-center text-slate-400">
          <p>Risk assessment not available for this visit.</p>
          {visit.message && <p className="text-sm mt-2 text-slate-500">{visit.message}</p>}
        </div>
      )}

      {risk?.isHighRisk && (
        <div className="mt-4 glass-card p-4 border-indigo-500/30 bg-indigo-500/5">
          <div className="flex items-center gap-2 mb-1">
            <Stethoscope size={16} className="text-indigo-400" />
            <p className="text-sm font-semibold text-indigo-300">Doctor Consultation Requested</p>
          </div>
          <p className="text-xs text-slate-400">
            A consultation has been automatically created in the doctor queue. Check the patient's profile for updates.
          </p>
          <Button variant="outline" size="sm" className="mt-3 border-indigo-500/40 text-indigo-400"
            onClick={() => navigate(`/patients/${visit.patientId}`)}>
            View Consultation Status →
          </Button>
        </div>
      )}
    </div>
  );
}
```

---

## src/pages/doctor/DoctorLoginPage.jsx

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Stethoscope, AlertCircle } from 'lucide-react';

export default function DoctorLoginPage() {
  const { login }  = useDoctorAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async ({ phone, password }) => {
    setErr('');
    try { await login(phone, password); navigate('/doctor/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Login failed. Check your credentials.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex">
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-navy-900 via-navy-800 to-indigo-900/30 flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-indigo-500 flex items-center justify-center">
            <Stethoscope size={20} className="text-white" />
          </div>
          <span className="font-display text-xl font-bold text-slate-100">Doctor Portal</span>
        </div>
        <div>
          <blockquote className="text-3xl font-display font-bold text-slate-100 leading-snug mb-4">
            Specialist care,<br />delivered instantly<br />across districts.
          </blockquote>
          <p className="text-slate-400 text-sm">
            Review high-risk cases in real-time, consult via<br />video, and close the loop on critical maternal health alerts.
          </p>
        </div>
        <div className="flex gap-6 text-xs font-mono text-slate-500">
          <span>PRIORITY QUEUE</span>
          <span>VIDEO CONSULT</span>
          <span>CLINICAL NOTES</span>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm animate-fade-in">
          <div className="mb-8">
            <p className="section-label text-indigo-400">Doctor Portal</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Sign in</h1>
          </div>

          {err && (
            <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
              <AlertCircle size={16} /> {err}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input label="Phone Number" type="tel" placeholder="9988776655"
              error={errors.phone?.message}
              {...register('phone', { required: 'Phone is required', pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid number' } })} />
            <Input label="Password" type="password" placeholder="••••••••"
              error={errors.password?.message}
              {...register('password', { required: 'Password is required' })} />
            <Button type="submit" loading={isSubmitting} className="w-full mt-2 bg-indigo-500 hover:bg-indigo-400 text-white shadow-indigo-500/20" size="lg">
              Sign In as Doctor
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            New doctor?{' '}
            <Link to="/doctor/signup" className="text-indigo-400 hover:text-indigo-300 font-medium">Register</Link>
          </p>
          <p className="text-center text-xs text-slate-600 mt-3">
            <Link to="/login" className="text-slate-500 hover:text-slate-400">← Worker portal</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorSignupPage.jsx

```jsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Stethoscope, AlertCircle } from 'lucide-react';

export default function DoctorSignupPage() {
  const { signup } = useDoctorAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    setErr('');
    try { await signup(data); navigate('/doctor/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Signup failed.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-fade-in">
        <div className="flex items-center gap-3 mb-8">
          <div className="h-10 w-10 rounded-xl bg-indigo-500 flex items-center justify-center">
            <Stethoscope size={20} className="text-white" />
          </div>
          <div>
            <p className="section-label text-indigo-400">Doctor Registration</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Create account</h1>
          </div>
        </div>

        {err && (
          <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
            <AlertCircle size={16} /> {err}
          </div>
        )}

        <div className="glass-card p-6">
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="grid grid-cols-2 gap-x-4">
              <div className="col-span-2">
                <Input label="Full Name *" placeholder="Dr. Priya Sharma"
                  error={errors.fullName?.message}
                  {...register('fullName', { required: 'Full name is required' })} />
              </div>
              <Input label="Phone *" type="tel" placeholder="9988776655"
                error={errors.phone?.message}
                {...register('phone', { required: true, pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid' } })} />
              <Input label="Email" type="email" placeholder="priya@hospital.in" {...register('email')} />
              <div className="col-span-2">
                <Input label="Password *" type="password" placeholder="Min. 8 characters"
                  error={errors.password?.message}
                  {...register('password', { required: true, minLength: { value: 8, message: 'Min 8 chars' } })} />
              </div>
              <div className="col-span-2">
                <Input label="Specialization" placeholder="Obstetrics & Gynaecology"
                  {...register('specialization')} />
              </div>
              <Input label="Hospital *" placeholder="District Hospital"
                error={errors.hospital?.message}
                {...register('hospital', { required: 'Hospital is required' })} />
              <Input label="District *" placeholder="Bangalore Rural"
                error={errors.district?.message}
                {...register('district', { required: 'District is required' })} />
              <div className="col-span-2">
                <Input label="Medical Council Reg. No." placeholder="KA-12345" {...register('registrationNo')} />
              </div>
            </div>
            <Button type="submit" loading={isSubmitting} className="w-full mt-2 bg-indigo-500 hover:bg-indigo-400 text-white" size="lg">
              Create Doctor Account
            </Button>
          </form>
        </div>
        <p className="text-center text-sm text-slate-500 mt-5">
          Already registered?{' '}
          <Link to="/doctor/login" className="text-indigo-400 hover:text-indigo-300 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorDashboardPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import { getQueue, getHistory } from '../../api/consultationApi';
import StatCard from '../../components/ui/StatCard';
import RiskBadge from '../../components/ui/RiskBadge';
import RiskDonutChart from '../../components/charts/RiskDonutChart';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import { ListOrdered, CheckCircle, Clock, AlertTriangle, ChevronRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function DoctorDashboardPage() {
  const { doctor } = useDoctorAuth();
  const navigate   = useNavigate();
  const [queue,   setQueue]   = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getQueue(), getHistory()])
      .then(([q, h]) => { setQueue(q); setHistory(h); })
      .finally(() => setLoading(false));
  }, []);

  // Auto-refresh queue every 30s
  useEffect(() => {
    const t = setInterval(() => getQueue().then(setQueue), 30000);
    return () => clearInterval(t);
  }, []);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  const critical  = queue.filter(c => c.riskLevel === 'CRITICAL');
  const completed = history.filter(c => c.status === 'COMPLETED');
  const chartData = [
    { name: 'CRITICAL', value: queue.filter(c => c.riskLevel === 'CRITICAL').length },
    { name: 'HIGH',     value: queue.filter(c => c.riskLevel === 'HIGH').length },
    { name: 'MEDIUM',   value: queue.filter(c => c.riskLevel === 'MEDIUM').length },
  ].filter(d => d.value > 0);

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="section-label text-indigo-400">Doctor Dashboard</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">
            Dr. {doctor?.fullName}
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">{doctor?.specialization} · {doctor?.hospital}</p>
        </div>
        <Button
          className="bg-indigo-500 hover:bg-indigo-400 text-white"
          onClick={() => navigate('/doctor/queue')}
        >
          <ListOrdered size={16} /> Open Queue
        </Button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="In Queue"      value={queue.length}     icon={ListOrdered}    accent="slate" />
        <StatCard label="Critical"      value={critical.length}  icon={AlertTriangle}  accent="critical" />
        <StatCard label="Completed"     value={completed.length} icon={CheckCircle}    accent="low" />
        <StatCard label="Total History" value={history.length}   icon={Clock}          accent="teal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Urgent queue preview */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <p className="section-label flex items-center gap-1.5">
              <AlertTriangle size={12} /> Pending Cases
            </p>
            <Button variant="ghost" size="sm" onClick={() => navigate('/doctor/queue')}>
              View all →
            </Button>
          </div>
          <div className="space-y-2">
            {queue.length === 0 ? (
              <div className="glass-card p-10 text-center">
                <CheckCircle size={32} className="text-teal-400 mx-auto mb-2" />
                <p className="text-slate-400 text-sm">Queue is clear. All cases attended to.</p>
              </div>
            ) : queue.slice(0, 6).map(c => (
              <button key={c.consultationId}
                onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}
                className="w-full glass-card p-4 flex items-center justify-between hover:border-indigo-500/40 transition-all group text-left">
                <div className="flex items-center gap-3">
                  {c.riskLevel === 'CRITICAL' && (
                    <span className="h-2 w-2 rounded-full bg-risk-critical animate-pulse flex-shrink-0" />
                  )}
                  <div>
                    <div className="flex items-center gap-2 mb-0.5">
                      <RiskBadge level={c.riskLevel} />
                      <span className="text-xs text-slate-500">{c.status}</span>
                    </div>
                    <p className="text-sm font-medium text-slate-200">{c.patientName || 'Patient'}</p>
                    <p className="text-xs text-slate-500">
                      {c.patientAge && `Age ${c.patientAge}`}
                      {c.gestationalWeeks && ` · ${c.gestationalWeeks}w GA`}
                      {c.healthCenter && ` · ${c.healthCenter}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-600">
                    {c.createdAt && formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                  </span>
                  <ChevronRight size={16} className="text-slate-600 group-hover:text-indigo-400 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Chart + recent history */}
        <div className="space-y-4">
          {chartData.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-2">Queue Distribution</p>
              <RiskDonutChart data={chartData} />
            </div>
          )}
          {history.length > 0 && (
            <div className="glass-card p-4">
              <p className="section-label mb-3">Recent Completions</p>
              <div className="space-y-2">
                {history.slice(0, 4).map(c => (
                  <button key={c.consultationId}
                    onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}
                    className="w-full flex items-center justify-between hover:bg-white/5 rounded-lg p-1.5 -mx-1.5 transition-colors group">
                    <div className="text-left">
                      <p className="text-sm text-slate-300 truncate">{c.patientName || 'Patient'}</p>
                      <p className="text-xs text-slate-500">{c.riskLevel}</p>
                    </div>
                    <ChevronRight size={14} className="text-slate-600 group-hover:text-slate-400 flex-shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## src/pages/doctor/QueuePage.jsx

```jsx
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getQueue, acceptConsult } from '../../api/consultationApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Button from '../../components/ui/Button';
import Spinner from '../../components/ui/Spinner';
import Toast from '../../components/ui/Toast';
import EmptyState from '../../components/ui/EmptyState';
import { RefreshCw, ChevronRight, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

function QueueSection({ title, color, items, onAccept, accepting, navigate }) {
  if (items.length === 0) return null;
  const border = { critical: 'border-l-risk-critical', high: 'border-l-risk-high', medium: 'border-l-risk-medium' };
  const text   = { critical: 'text-risk-critical', high: 'text-risk-high', medium: 'text-risk-medium' };
  return (
    <div className="mb-6">
      <p className={`text-xs font-mono font-bold uppercase tracking-widest mb-3 ${text[color]}`}>
        {title} · {items.length}
      </p>
      <div className="space-y-2">
        {items.map(c => (
          <div key={c.consultationId}
            className={`glass-card p-4 border-l-4 ${border[color]} hover:bg-white/[0.02] transition-colors`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                  <RiskBadge level={c.riskLevel} />
                  <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                    ${c.status === 'ACCEPTED'    ? 'text-indigo-400 bg-indigo-400/10'
                    : c.status === 'IN_PROGRESS' ? 'text-teal-400 bg-teal-400/10 animate-pulse'
                    : 'text-slate-400 bg-white/5'}`}>
                    {c.status}
                  </span>
                  <span className="text-xs text-slate-600">
                    {c.createdAt && formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                  </span>
                </div>
                <p className="font-semibold text-slate-100">{c.patientName || 'Patient'}</p>
                <p className="text-sm text-slate-400">
                  {[c.patientAge && `Age ${c.patientAge}`, c.gestationalWeeks && `${c.gestationalWeeks}w GA`, c.district].filter(Boolean).join(' · ')}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  ANC Worker: {c.workerName} · {c.healthCenter}
                </p>
                {c.detectedRisks?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {c.detectedRisks.slice(0, 3).map((r, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20">
                        {r}
                      </span>
                    ))}
                    {c.detectedRisks.length > 3 && (
                      <span className="text-[10px] text-slate-500">+{c.detectedRisks.length - 3} more</span>
                    )}
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-2 flex-shrink-0">
                {c.status === 'PENDING' && (
                  <Button size="sm" loading={accepting === c.consultationId}
                    className="bg-indigo-500 hover:bg-indigo-400 text-white"
                    onClick={() => onAccept(c.consultationId)}>
                    Accept
                  </Button>
                )}
                <Button size="sm" variant="secondary"
                  onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}>
                  Open <ChevronRight size={14} />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function QueuePage() {
  const navigate  = useNavigate();
  const [queue,     setQueue]     = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [accepting, setAccepting] = useState(null);
  const [toast,     setToast]     = useState(null);

  const fetch = useCallback(() => {
    return getQueue().then(setQueue).finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetch(); }, [fetch]);
  useEffect(() => {
    const t = setInterval(fetch, 30000);
    return () => clearInterval(t);
  }, [fetch]);

  const handleAccept = async (id) => {
    setAccepting(id);
    try {
      await acceptConsult(id);
      await fetch();
      setToast({ msg: 'Case accepted successfully', type: 'success' });
      navigate(`/doctor/consultations/${id}`);
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to accept case', type: 'error' });
    } finally { setAccepting(null); }
  };

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  const critical = queue.filter(c => c.riskLevel === 'CRITICAL');
  const high     = queue.filter(c => c.riskLevel === 'HIGH');
  const medium   = queue.filter(c => c.riskLevel === 'MEDIUM');

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="section-label text-indigo-400">Teleconsultation</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Priority Queue</h1>
          <p className="text-slate-400 text-sm">
            {queue.length} case{queue.length !== 1 ? 's' : ''} · auto-refreshes every 30s
          </p>
        </div>
        <Button variant="secondary" onClick={() => { setLoading(true); fetch(); }}>
          <RefreshCw size={15} /> Refresh
        </Button>
      </div>

      {queue.length === 0 ? (
        <EmptyState
          icon={<CheckCircle size={48} className="text-teal-400" />}
          title="Queue is clear"
          sub="All high-risk cases have been attended to."
        />
      ) : (
        <>
          <QueueSection title="🚨 Critical" color="critical" items={critical}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
          <QueueSection title="⚠ High Risk" color="high"     items={high}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
          <QueueSection title="⚡ Medium Risk" color="medium" items={medium}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
        </>
      )}

      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
```

---

## src/pages/doctor/ConsultationPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { getConsult, startCall, completeConsult } from '../../api/consultationApi';
import VideoRoom from '../../components/video/VideoRoom';
import RiskBadge from '../../components/ui/RiskBadge';
import ConfidenceBar from '../../components/visits/ConfidenceBar';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Spinner from '../../components/ui/Spinner';
import Toast from '../../components/ui/Toast';
import { ArrowLeft, Video, VideoOff, CheckCircle, AlertTriangle, Phone, MapPin, User } from 'lucide-react';

function DataCard({ title, icon: Icon, children }) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-2 section-label mb-3">
        {Icon && <Icon size={13} />} {title}
      </div>
      {children}
    </div>
  );
}

function InfoRow({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex justify-between items-start py-1.5 border-b border-white/5 last:border-0">
      <span className="text-xs text-slate-500 flex-shrink-0 w-28">{label}</span>
      <span className="text-sm text-slate-200 text-right font-medium">{value}</span>
    </div>
  );
}

export default function ConsultationPage() {
  const { id }   = useParams();
  const navigate = useNavigate();
  const [consult,    setConsult]    = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [callBusy,   setCallBusy]   = useState(false);
  const [inCall,     setInCall]     = useState(false);
  const [toast,      setToast]      = useState(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const reload = () => getConsult(id).then(d => {
    setConsult(d);
    if (d.status === 'IN_PROGRESS' && d.roomUrl) setInCall(true);
  }).finally(() => setLoading(false));

  useEffect(() => { reload(); }, [id]);

  const handleStartCall = async () => {
    setCallBusy(true);
    try {
      const updated = await startCall(id);
      setConsult(updated);
      setInCall(true);
      setToast({ msg: 'Video room created. Worker has been notified.', type: 'success' });
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to start call', type: 'error' });
    } finally { setCallBusy(false); }
  };

  const handleComplete = async (notes) => {
    try {
      await completeConsult(id, notes);
      setToast({ msg: 'Consultation completed successfully', type: 'success' });
      setTimeout(() => navigate('/doctor/queue'), 1500);
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to complete', type: 'error' });
    }
  };

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!consult) return <div className="p-8 text-slate-400">Consultation not found.</div>;

  const c = consult;
  const isCompleted = c.status === 'COMPLETED';

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate('/doctor/queue')}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-indigo-400 mb-2 transition-colors">
            <ArrowLeft size={14} /> Back to Queue
          </button>
          <div className="flex items-center gap-3">
            <RiskBadge level={c.riskLevel} large />
            <h1 className="font-display text-2xl font-bold text-slate-100">
              {c.patientName || 'Patient'}
            </h1>
            <span className={`text-xs px-3 py-1 rounded-full font-mono font-semibold
              ${isCompleted ? 'text-teal-400 bg-teal-400/10'
              : c.status === 'IN_PROGRESS' ? 'text-risk-medium bg-risk-medium/10 animate-pulse'
              : 'text-indigo-400 bg-indigo-400/10'}`}>
              {c.status}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT: Patient + Risk info */}
        <div className="space-y-4">
          <DataCard title="Patient Details" icon={User}>
            <InfoRow label="Name"            value={c.patientName} />
            <InfoRow label="Age"             value={c.patientAge ? `${c.patientAge} years` : null} />
            <InfoRow label="Gestational Age" value={c.gestationalWeeks ? `${c.gestationalWeeks} weeks` : null} />
            <InfoRow label="Blood Group"     value={c.bloodGroup} />
            <InfoRow label="Phone"           value={c.patientPhone} />
            <InfoRow label="Location"        value={[c.village, c.district].filter(Boolean).join(', ')} />
          </DataCard>

          <DataCard title="AI Risk Assessment" icon={AlertTriangle}>
            <div className="mb-3">
              <ConfidenceBar value={c.confidence} />
            </div>
            {c.detectedRisks?.length > 0 && (
              <div className="mb-3">
                <p className="text-xs text-slate-500 mb-1.5">Detected Risk Factors:</p>
                <div className="flex flex-wrap gap-1.5">
                  {c.detectedRisks.map((r, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20">
                      {r}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {c.explanation && (
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <p className="text-xs text-slate-400 leading-relaxed">{c.explanation}</p>
              </div>
            )}
            {c.recommendation && (
              <div className="mt-3 p-3 rounded-xl bg-teal-500/10 border border-teal-500/20">
                <p className="text-xs font-mono text-teal-400 mb-1">RECOMMENDATION</p>
                <p className="text-sm text-teal-200 font-medium">{c.recommendation}</p>
              </div>
            )}
          </DataCard>

          <DataCard title="ANC Worker" icon={Phone}>
            <InfoRow label="Worker"        value={c.workerName} />
            <InfoRow label="Phone"         value={c.workerPhone} />
            <InfoRow label="Health Center" value={c.healthCenter} />
          </DataCard>
        </div>

        {/* RIGHT: Video + Notes */}
        <div className="space-y-4">

          {/* Video call */}
          <DataCard title="Video Teleconsultation" icon={Video}>
            {isCompleted ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <CheckCircle size={40} className="text-teal-400 mb-3" />
                <p className="text-slate-300 font-medium">Consultation Completed</p>
                <p className="text-xs text-slate-500 mt-1">Call session has ended</p>
              </div>
            ) : inCall && c.roomUrl && c.doctorToken ? (
              <VideoRoom
                roomUrl={c.roomUrl}
                token={c.doctorToken}
                onLeave={() => setInCall(false)}
              />
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <div className="h-16 w-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4">
                  {c.status === 'ACCEPTED' ? (
                    <Video size={28} className="text-indigo-400" />
                  ) : (
                    <VideoOff size={28} className="text-slate-500" />
                  )}
                </div>
                <p className="text-slate-300 text-sm font-medium mb-1">
                  {c.status === 'ACCEPTED' ? 'Ready to start' : 'Accept case to begin'}
                </p>
                <p className="text-xs text-slate-500 mb-4">
                  {c.status === 'ACCEPTED'
                    ? 'Worker will receive a notification to join'
                    : 'Go to queue and accept this case first'}
                </p>
                <Button
                  onClick={handleStartCall}
                  loading={callBusy}
                  disabled={c.status !== 'ACCEPTED'}
                  className="bg-indigo-500 hover:bg-indigo-400 text-white"
                >
                  <Video size={16} /> Start Video Call
                </Button>
              </div>
            )}
          </DataCard>

          {/* Notes form or completed notes */}
          {isCompleted ? (
            <DataCard title="Completed Notes" icon={CheckCircle}>
              {c.doctorNotes && (
                <div className="mb-3">
                  <p className="text-xs text-slate-500 mb-1">Clinical Notes</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{c.doctorNotes}</p>
                </div>
              )}
              {c.diagnosis && (
                <div className="mb-3">
                  <p className="text-xs text-slate-500 mb-1">Diagnosis</p>
                  <p className="text-sm text-slate-300 font-medium">{c.diagnosis}</p>
                </div>
              )}
              {c.actionPlan && (
                <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20">
                  <p className="text-xs font-mono text-teal-400 mb-1">ACTION PLAN</p>
                  <p className="text-sm text-teal-200 whitespace-pre-line">{c.actionPlan}</p>
                </div>
              )}
            </DataCard>
          ) : (
            <DataCard title="Consultation Notes" icon={CheckCircle}>
              <form onSubmit={handleSubmit(handleComplete)} noValidate>
                <Input label="Clinical Notes *" type="textarea" rows={3}
                  placeholder="Describe findings, patient condition, interventions..."
                  error={errors.doctorNotes?.message}
                  {...register('doctorNotes', { required: 'Clinical notes are required' })} />
                <Input label="Diagnosis" type="textarea" rows={2}
                  placeholder="e.g. Severe Pre-eclampsia with anaemia"
                  {...register('diagnosis')} />
                <Input label="Action Plan *" type="textarea" rows={3}
                  placeholder={"1. Immediate referral to CEmOC\n2. IV MgSO4\n3. Blood transfusion"}
                  error={errors.actionPlan?.message}
                  {...register('actionPlan', { required: 'Action plan is required' })} />
                <Button type="submit" loading={isSubmitting}
                  className="w-full mt-2 bg-teal-500 hover:bg-teal-400 text-navy-950 font-semibold">
                  <CheckCircle size={16} /> Complete Consultation
                </Button>
              </form>
            </DataCard>
          )}
        </div>
      </div>

      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
```

---

## src/pages/doctor/HistoryPage.jsx

```jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory } from '../../api/consultationApi';
import { useApi } from '../../hooks/useApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Spinner from '../../components/ui/Spinner';
import EmptyState from '../../components/ui/EmptyState';
import { ChevronRight, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

export default function HistoryPage() {
  const navigate = useNavigate();
  const { data: history, loading, run } = useApi(getHistory);
  useEffect(() => { run(); }, []);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-6">
        <p className="section-label text-indigo-400">Consultation History</p>
        <h1 className="font-display text-2xl font-bold text-slate-100">Past Consultations</h1>
        <p className="text-slate-400 text-sm">{history?.length || 0} total</p>
      </div>

      {!history?.length ? (
        <EmptyState icon="📂" title="No consultations yet" sub="Completed consultations will appear here." />
      ) : (
        <div className="space-y-2">
          {history.map(c => (
            <button key={c.consultationId}
              onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}
              className="w-full glass-card p-4 flex items-center justify-between hover:border-indigo-500/30 transition-all group text-left">
              <div className="flex items-center gap-4">
                <div className={`h-9 w-9 rounded-xl flex items-center justify-center flex-shrink-0
                  ${c.status === 'COMPLETED' ? 'bg-teal-500/20' : 'bg-white/5'}`}>
                  <CheckCircle size={18} className={c.status === 'COMPLETED' ? 'text-teal-400' : 'text-slate-600'} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <RiskBadge level={c.riskLevel} />
                    <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                      ${c.status === 'COMPLETED' ? 'text-teal-400 bg-teal-400/10' : 'text-slate-400 bg-white/5'}`}>
                      {c.status}
                    </span>
                  </div>
                  <p className="font-medium text-slate-200">{c.patientName || 'Patient'}</p>
                  <p className="text-xs text-slate-500">
                    {[c.patientAge && `Age ${c.patientAge}`, c.gestationalWeeks && `${c.gestationalWeeks}w`, c.district].filter(Boolean).join(' · ')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                {c.completedAt && (
                  <span className="text-xs text-slate-600">
                    {format(new Date(c.completedAt), 'dd MMM yyyy')}
                  </span>
                )}
                <ChevronRight size={16} className="text-slate-600 group-hover:text-indigo-400 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## src/App.jsx

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider }       from './context/AuthContext';
import { DoctorAuthProvider } from './context/DoctorAuthContext';
import WorkerRoute  from './routes/WorkerRoute';
import DoctorRoute  from './routes/DoctorRoute';
import WorkerLayout from './components/layout/WorkerLayout';
import DoctorLayout from './components/layout/DoctorLayout';

// Worker pages
import LoginPage         from './pages/worker/LoginPage';
import SignupPage        from './pages/worker/SignupPage';
import DashboardPage     from './pages/worker/DashboardPage';
import PatientListPage   from './pages/worker/PatientListPage';
import PatientCreatePage from './pages/worker/PatientCreatePage';
import PatientDetailPage from './pages/worker/PatientDetailPage';
import VisitFormPage     from './pages/worker/VisitFormPage';
import VisitResultPage   from './pages/worker/VisitResultPage';

// Doctor pages
import DoctorLoginPage    from './pages/doctor/DoctorLoginPage';
import DoctorSignupPage   from './pages/doctor/DoctorSignupPage';
import DoctorDashboard    from './pages/doctor/DoctorDashboardPage';
import QueuePage          from './pages/doctor/QueuePage';
import ConsultationPage   from './pages/doctor/ConsultationPage';
import HistoryPage        from './pages/doctor/HistoryPage';

export default function App() {
  return (
    <AuthProvider>
      <DoctorAuthProvider>
        <BrowserRouter>
          <Routes>

            {/* ── Public: Worker ─────────────────────────────── */}
            <Route path="/login"  element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* ── Protected: Worker ──────────────────────────── */}
            <Route element={<WorkerRoute />}>
              <Route element={<WorkerLayout />}>
                <Route path="/dashboard"                 element={<DashboardPage />} />
                <Route path="/patients"                  element={<PatientListPage />} />
                <Route path="/patients/new"              element={<PatientCreatePage />} />
                <Route path="/patients/:id"              element={<PatientDetailPage />} />
                <Route path="/visits/new/:patientId"     element={<VisitFormPage />} />
                <Route path="/visits/:visitId"           element={<VisitResultPage />} />
              </Route>
            </Route>

            {/* ── Public: Doctor ─────────────────────────────── */}
            <Route path="/doctor/login"  element={<DoctorLoginPage />} />
            <Route path="/doctor/signup" element={<DoctorSignupPage />} />

            {/* ── Protected: Doctor ──────────────────────────── */}
            <Route element={<DoctorRoute />}>
              <Route element={<DoctorLayout />}>
                <Route path="/doctor/dashboard"                     element={<DoctorDashboard />} />
                <Route path="/doctor/queue"                         element={<QueuePage />} />
                <Route path="/doctor/consultations/:id"             element={<ConsultationPage />} />
                <Route path="/doctor/history"                       element={<HistoryPage />} />
              </Route>
            </Route>

            {/* ── Defaults ───────────────────────────────────── */}
            <Route path="/"   element={<Navigate to="/login"        replace />} />
            <Route path="*"   element={<Navigate to="/login"        replace />} />

          </Routes>
        </BrowserRouter>
      </DoctorAuthProvider>
    </AuthProvider>
  );
}
```

---

## Quick Start

```bash
# 1. Create project
npm create vite@latest anc-portal -- --template react
cd anc-portal

# 2. Install all dependencies
npm install react-router-dom axios react-hook-form recharts lucide-react date-fns @daily-co/daily-js clsx

# 3. Install dev tools
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Create all files above in src/

# 5. Start dev server
npm run dev
# → http://localhost:5173
```

---

## Complete File Checklist

```
✅ .env
✅ index.html                     (Google Fonts: Syne + DM Sans + JetBrains Mono)
✅ vite.config.js                 (proxy /api → :8080)
✅ tailwind.config.js             (navy/teal/risk color system + animation)
✅ src/index.css                  (glass, glass-card, risk-* utilities)
✅ src/main.jsx
✅ src/App.jsx                    (all routes, both portals)

API
✅ src/api/axiosInstance.js       (JWT attach + 401 auto-redirect)
✅ src/api/authApi.js             (signup, login, me)
✅ src/api/patientApi.js          (create, list, get)
✅ src/api/visitApi.js            (register, get, patient visits, high-risk, critical)
✅ src/api/doctorApi.js           (signup, login, me)
✅ src/api/consultationApi.js     (queue, get, accept, start-call, complete, history)

Auth
✅ src/context/AuthContext.jsx    (worker: login/signup/logout + localStorage)
✅ src/context/DoctorAuthContext.jsx
✅ src/hooks/useAuth.js
✅ src/hooks/useDoctorAuth.js
✅ src/hooks/useApi.js            (loading/error/data wrapper)
✅ src/routes/WorkerRoute.jsx
✅ src/routes/DoctorRoute.jsx

UI Components
✅ src/components/ui/Spinner.jsx
✅ src/components/ui/Button.jsx   (primary/secondary/danger/ghost/outline variants)
✅ src/components/ui/Input.jsx    (text + textarea, dark theme)
✅ src/components/ui/RiskBadge.jsx (CRITICAL pulse, colors)
✅ src/components/ui/StatCard.jsx
✅ src/components/ui/EmptyState.jsx
✅ src/components/ui/Toast.jsx    (auto-dismiss, success/error)
✅ src/components/ui/Modal.jsx    (Escape to close)

Layout
✅ src/components/layout/WorkerLayout.jsx (navy sidebar, teal accents)
✅ src/components/layout/DoctorLayout.jsx (navy sidebar, indigo accents)

Specialty
✅ src/components/charts/RiskDonutChart.jsx (Recharts)
✅ src/components/visits/StepWizard.jsx
✅ src/components/visits/RiskReport.jsx
✅ src/components/visits/ConfidenceBar.jsx
✅ src/components/video/VideoRoom.jsx       (@daily-co/daily-js iframe)

Worker Pages (8)
✅ src/pages/worker/LoginPage.jsx     (split hero layout)
✅ src/pages/worker/SignupPage.jsx
✅ src/pages/worker/DashboardPage.jsx  (stats + critical alerts + risk chart)
✅ src/pages/worker/PatientListPage.jsx (search filter)
✅ src/pages/worker/PatientCreatePage.jsx
✅ src/pages/worker/PatientDetailPage.jsx (visits + consultations tabs)
✅ src/pages/worker/VisitFormPage.jsx  (7-step wizard, all DTO fields)
✅ src/pages/worker/VisitResultPage.jsx

Doctor Pages (6)
✅ src/pages/doctor/DoctorLoginPage.jsx (split hero layout)
✅ src/pages/doctor/DoctorSignupPage.jsx
✅ src/pages/doctor/DoctorDashboardPage.jsx (stats + queue preview + chart)
✅ src/pages/doctor/QueuePage.jsx      (CRITICAL/HIGH/MEDIUM sections, 30s refresh)
✅ src/pages/doctor/ConsultationPage.jsx (full case + Daily.co video + notes)
✅ src/pages/doctor/HistoryPage.jsx
```

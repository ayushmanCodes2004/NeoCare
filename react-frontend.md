# ANC Worker React Frontend — Complete Implementation
## JWT Auth + Token Management + All Pages and Components

**Stack:** React 18 + React Router v6 + Axios + Context API + TailwindCSS

---

## What This Builds

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APP SCREENS                                  │
│                                                                     │
│  /login          → Worker Login (phone + password)                  │
│  /signup         → Worker Signup (fullName, phone, email, etc.)     │
│                                                                     │
│  /dashboard      → Summary stats + high risk alerts                 │
│  /patients       → Patient list (this worker's patients only)       │
│  /patients/new   → Register new patient                             │
│  /patients/:id   → Patient profile + visit history                  │
│  /visits/new/:id → 7-step ANC visit form → submits to FastAPI       │
│  /visits/:id     → Visit result: risk level, detected risks, etc.   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
anc-frontend/
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
    │   ├── axiosInstance.js        ← Axios with JWT interceptor
    │   ├── authApi.js              ← signup, login, getMe
    │   ├── patientApi.js           ← createPatient, getPatients, getPatientById
    │   └── visitApi.js             ← registerVisit, getVisits, getHighRisk
    │
    ├── context/
    │   └── AuthContext.jsx         ← global auth state, login(), logout()
    │
    ├── hooks/
    │   ├── useAuth.js              ← consume AuthContext
    │   └── useApi.js               ← loading/error wrapper for API calls
    │
    ├── routes/
    │   └── ProtectedRoute.jsx      ← redirect to /login if no token
    │
    ├── pages/
    │   ├── LoginPage.jsx
    │   ├── SignupPage.jsx
    │   ├── DashboardPage.jsx
    │   ├── PatientListPage.jsx
    │   ├── PatientCreatePage.jsx
    │   ├── PatientDetailPage.jsx
    │   ├── AncVisitFormPage.jsx    ← 7-step form
    │   └── VisitResultPage.jsx     ← displays risk assessment
    │
    └── components/
        ├── layout/
        │   ├── AppLayout.jsx       ← sidebar + topbar wrapper
        │   ├── Sidebar.jsx
        │   └── Topbar.jsx
        ├── ui/
        │   ├── InputField.jsx
        │   ├── Button.jsx
        │   ├── Badge.jsx           ← CRITICAL / HIGH / MEDIUM / LOW
        │   ├── Spinner.jsx
        │   └── ErrorAlert.jsx
        ├── patients/
        │   └── PatientCard.jsx
        └── visits/
            ├── RiskBanner.jsx      ← big CRITICAL/HIGH alert banner
            ├── DetectedRisksList.jsx
            └── VisitStepIndicator.jsx
```

---

## package.json

```json
{
  "name": "anc-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7",
    "react-hook-form": "^7.51.0",
    "date-fns": "^3.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.1.4",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.18"
  }
}
```

---

## tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary:  { DEFAULT: '#2563eb', dark: '#1d4ed8' },
        critical: '#dc2626',
        high:     '#ea580c',
        medium:   '#ca8a04',
        low:      '#16a34a',
      }
    },
  },
  plugins: [],
}
```

---

## postcss.config.js

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## .env

```
VITE_API_BASE_URL=http://localhost:8080
```

---

## src/api/axiosInstance.js

```js
import axios from 'axios';

/**
 * Central Axios instance.
 *
 * REQUEST INTERCEPTOR:
 *   Automatically attaches JWT from localStorage to every request
 *   as: Authorization: Bearer <token>
 *   This means individual API functions never need to set the header.
 *
 * RESPONSE INTERCEPTOR:
 *   If any request gets a 401 (token expired or invalid):
 *   - Clear localStorage
 *   - Redirect to /login
 *   This handles token expiry globally without each page needing to check.
 */
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor: attach JWT ───────────────────────────────────────────
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('anc_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle 401 globally ────────────────────────────────
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect
      localStorage.removeItem('anc_token');
      localStorage.removeItem('anc_worker');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## src/api/authApi.js

```js
import axiosInstance from './axiosInstance';

/**
 * Auth API — matches AuthController.java endpoints
 *
 * POST /api/auth/signup  → WorkerSignupRequestDTO → AuthResponseDTO
 * POST /api/auth/login   → WorkerLoginRequestDTO  → AuthResponseDTO
 * GET  /api/auth/me      → AuthResponseDTO
 */

export const signup = async (data) => {
  // data: { fullName, phone, email, password, healthCenter, district }
  const response = await axiosInstance.post('/api/auth/signup', data);
  return response.data; // AuthResponseDTO: { token, workerId, fullName, phone, ... }
};

export const login = async (data) => {
  // data: { phone, password }
  const response = await axiosInstance.post('/api/auth/login', data);
  return response.data; // AuthResponseDTO: { token, workerId, fullName, phone, ... }
};

export const getMe = async () => {
  const response = await axiosInstance.get('/api/auth/me');
  return response.data; // AuthResponseDTO (no token field)
};
```

---

## src/api/patientApi.js

```js
import axiosInstance from './axiosInstance';

/**
 * Patient API — matches PatientController.java endpoints
 *
 * POST /api/patients              → PatientCreateRequestDTO → PatientResponseDTO
 * GET  /api/patients              → PatientResponseDTO[]
 * GET  /api/patients/{patientId}  → PatientResponseDTO
 */

export const createPatient = async (data) => {
  // data: { fullName, phone, age, address, village, district, lmpDate, eddDate, bloodGroup }
  const response = await axiosInstance.post('/api/patients', data);
  return response.data; // PatientResponseDTO
};

export const getMyPatients = async () => {
  const response = await axiosInstance.get('/api/patients');
  return response.data; // PatientResponseDTO[]
};

export const getPatientById = async (patientId) => {
  const response = await axiosInstance.get(`/api/patients/${patientId}`);
  return response.data; // PatientResponseDTO
};
```

---

## src/api/visitApi.js

```js
import axiosInstance from './axiosInstance';

/**
 * ANC Visit API — matches AncVisitController.java endpoints
 *
 * POST /api/anc/register-visit               → AncVisitRequestDTO → AncVisitResponseDTO
 * GET  /api/anc/patients/{patientId}/visits  → AncVisitEntity[]
 * GET  /api/anc/visits/{visitId}             → AncVisitEntity
 * GET  /api/anc/visits/high-risk             → AncVisitEntity[]
 * GET  /api/anc/visits/critical              → AncVisitEntity[]
 */

export const registerVisit = async (data) => {
  /**
   * data shape — matches AncVisitRequestDTO:
   * {
   *   patientId: "uuid",
   *   structured_data: {
   *     patient_info:      { age, gestationalWeeks },
   *     medical_history:   { previousLSCS, smoking, diabetes, ... },
   *     vitals:            { heightCm, bmi, bpSystolic, bpDiastolic },
   *     lab_reports:       { hemoglobin, rhNegative, hivPositive, urineProtein, ... },
   *     obstetric_history: { birthOrder, interPregnancyInterval, stillbirthCount, ... },
   *     pregnancy_details: { twinPregnancy, placentaPrevia, malpresentation, ... },
   *     current_symptoms:  { headache, visualDisturbance, convulsions, ... }
   *   }
   * }
   *
   * Response — AncVisitResponseDTO:
   * {
   *   visitId, patientId, status, message, savedAt,
   *   riskAssessment: {
   *     isHighRisk, riskLevel, detectedRisks[], explanation,
   *     confidence, recommendation, age, gestationalWeeks
   *   }
   * }
   */
  const response = await axiosInstance.post('/api/anc/register-visit', data);
  return response.data;
};

export const getPatientVisits = async (patientId) => {
  const response = await axiosInstance.get(`/api/anc/patients/${patientId}/visits`);
  return response.data;
};

export const getVisitById = async (visitId) => {
  const response = await axiosInstance.get(`/api/anc/visits/${visitId}`);
  return response.data;
};

export const getHighRiskVisits = async () => {
  const response = await axiosInstance.get('/api/anc/visits/high-risk');
  return response.data;
};

export const getCriticalVisits = async () => {
  const response = await axiosInstance.get('/api/anc/visits/critical');
  return response.data;
};
```

---

## src/context/AuthContext.jsx

```jsx
import { createContext, useState, useEffect, useCallback } from 'react';
import { login as apiLogin, signup as apiSignup } from '../api/authApi';

/**
 * AuthContext — global authentication state.
 *
 * Provides:
 *   worker      → { workerId, fullName, phone, email, healthCenter, district }
 *   token       → JWT string
 *   isLoading   → true while checking localStorage on first load
 *   login()     → calls POST /api/auth/login, stores token, sets worker
 *   signup()    → calls POST /api/auth/signup, stores token, sets worker
 *   logout()    → clears localStorage + state, redirects to /login
 *
 * TOKEN STORAGE STRATEGY:
 *   - JWT stored in localStorage under key 'anc_token'
 *   - Worker info stored in localStorage under key 'anc_worker' (JSON)
 *   - On app load: reads both from localStorage to restore session
 *   - axiosInstance reads 'anc_token' on every request automatically
 */

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [worker, setWorker]     = useState(null);
  const [token, setToken]       = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // ── Restore session from localStorage on app load ────────────────────────
  useEffect(() => {
    const storedToken  = localStorage.getItem('anc_token');
    const storedWorker = localStorage.getItem('anc_worker');

    if (storedToken && storedWorker) {
      try {
        setToken(storedToken);
        setWorker(JSON.parse(storedWorker));
      } catch {
        // Corrupted data — clear it
        localStorage.removeItem('anc_token');
        localStorage.removeItem('anc_worker');
      }
    }
    setIsLoading(false);
  }, []);

  // ── Persist auth data to localStorage ───────────────────────────────────
  const persistAuth = (authResponse) => {
    const { token, ...workerInfo } = authResponse;
    localStorage.setItem('anc_token', token);
    localStorage.setItem('anc_worker', JSON.stringify(workerInfo));
    setToken(token);
    setWorker(workerInfo);
  };

  // ── Login ────────────────────────────────────────────────────────────────
  const login = useCallback(async (phone, password) => {
    const authResponse = await apiLogin({ phone, password });
    persistAuth(authResponse);
    return authResponse;
  }, []);

  // ── Signup ───────────────────────────────────────────────────────────────
  const signup = useCallback(async (formData) => {
    const authResponse = await apiSignup(formData);
    persistAuth(authResponse);
    return authResponse;
  }, []);

  // ── Logout ───────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    localStorage.removeItem('anc_token');
    localStorage.removeItem('anc_worker');
    setToken(null);
    setWorker(null);
    window.location.href = '/login';
  }, []);

  const value = {
    worker,
    token,
    isLoading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

## src/hooks/useAuth.js

```js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Convenience hook to consume AuthContext.
 *
 * Usage:
 *   const { worker, login, logout, isAuthenticated } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside <AuthProvider>');
  }
  return context;
}
```

---

## src/hooks/useApi.js

```js
import { useState, useCallback } from 'react';

/**
 * Generic hook to wrap any async API call with loading + error state.
 *
 * Usage:
 *   const { execute, data, loading, error } = useApi(getMyPatients);
 *   useEffect(() => { execute(); }, []);
 *
 * Or with arguments:
 *   const { execute, data, loading, error } = useApi(getPatientById);
 *   execute(patientId);
 */
export function useApi(apiFunction) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error   ||
        err.message                 ||
        'Something went wrong';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  return { execute, data, loading, error, setData };
}
```

---

## src/routes/ProtectedRoute.jsx

```jsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Spinner from '../components/ui/Spinner';

/**
 * Wraps protected routes.
 * If no token → redirect to /login.
 * While checking localStorage → show spinner.
 *
 * Usage in App.jsx:
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<DashboardPage />} />
 *     ...
 *   </Route>
 */
export default function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

---

## src/components/ui/Spinner.jsx

```jsx
export default function Spinner({ size = 'md' }) {
  const sizes = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' };
  return (
    <div className={`animate-spin rounded-full border-4 border-blue-200 border-t-blue-600 ${sizes[size]}`} />
  );
}
```

---

## src/components/ui/ErrorAlert.jsx

```jsx
export default function ErrorAlert({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-4">
      <span className="text-red-500 mt-0.5">⚠</span>
      <p className="flex-1 text-sm">{message}</p>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-400 hover:text-red-600 text-lg leading-none">×</button>
      )}
    </div>
  );
}
```

---

## src/components/ui/InputField.jsx

```jsx
/**
 * Reusable form input — works with react-hook-form register().
 *
 * Usage:
 *   <InputField
 *     label="Phone Number"
 *     type="tel"
 *     placeholder="9876543210"
 *     error={errors.phone?.message}
 *     {...register('phone')}
 *   />
 */
import { forwardRef } from 'react';

const InputField = forwardRef(function InputField(
  { label, error, type = 'text', className = '', ...props },
  ref
) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={`w-full px-3 py-2 border rounded-lg text-sm shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${error ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'}
          ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </div>
  );
});

export default InputField;
```

---

## src/components/ui/Button.jsx

```jsx
import Spinner from './Spinner';

/**
 * Button variants: primary | secondary | danger | ghost
 *
 * Usage:
 *   <Button loading={submitting} onClick={handleSubmit}>Save Patient</Button>
 *   <Button variant="danger" onClick={logout}>Logout</Button>
 */
export default function Button({
  children,
  variant = 'primary',
  loading = false,
  disabled = false,
  type = 'button',
  className = '',
  ...props
}) {
  const base = 'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary:   'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300',
    danger:    'bg-red-600 text-white hover:bg-red-700',
    ghost:     'text-gray-600 hover:bg-gray-100',
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`${base} ${variants[variant]} ${className}`}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}
```

---

## src/components/ui/Badge.jsx

```jsx
/**
 * Risk level badge — maps riskLevel to colour.
 *
 * Usage:
 *   <Badge riskLevel="CRITICAL" />
 *   <Badge riskLevel="HIGH" />
 *   <Badge riskLevel="MEDIUM" />
 *   <Badge riskLevel="LOW" />
 */
export default function Badge({ riskLevel, className = '' }) {
  const styles = {
    CRITICAL: 'bg-red-100 text-red-800 border-red-300',
    HIGH:     'bg-orange-100 text-orange-800 border-orange-300',
    MEDIUM:   'bg-yellow-100 text-yellow-800 border-yellow-300',
    LOW:      'bg-green-100 text-green-800 border-green-300',
  };

  const style = styles[riskLevel] || 'bg-gray-100 text-gray-600 border-gray-300';

  return (
    <span className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full border ${style} ${className}`}>
      {riskLevel || 'UNKNOWN'}
    </span>
  );
}
```

---

## src/components/visits/RiskBanner.jsx

```jsx
import Badge from '../ui/Badge';

/**
 * Big alert banner shown at the top of the VisitResultPage.
 * Red/orange/yellow/green depending on riskLevel.
 *
 * Props:
 *   isHighRisk   boolean
 *   riskLevel    "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
 *   recommendation  string
 */
export default function RiskBanner({ isHighRisk, riskLevel, recommendation }) {
  const bgStyles = {
    CRITICAL: 'bg-red-600 text-white',
    HIGH:     'bg-orange-500 text-white',
    MEDIUM:   'bg-yellow-400 text-gray-900',
    LOW:      'bg-green-500 text-white',
  };

  const bg = bgStyles[riskLevel] || 'bg-gray-400 text-white';

  return (
    <div className={`rounded-xl p-5 mb-6 ${bg}`}>
      <div className="flex items-center gap-3 mb-2">
        {isHighRisk && (
          <span className="text-2xl">🚨</span>
        )}
        <h2 className="text-xl font-bold">
          Risk Level: {riskLevel}
        </h2>
        <Badge riskLevel={riskLevel} className="ml-auto" />
      </div>
      {recommendation && (
        <p className="text-sm font-medium mt-1 opacity-90">{recommendation}</p>
      )}
    </div>
  );
}
```

---

## src/components/visits/DetectedRisksList.jsx

```jsx
/**
 * Renders the detectedRisks[] array from FastAPI response.
 *
 * Props:
 *   risks  string[]  e.g. ["Severe Anaemia", "Twin Pregnancy", ...]
 */
export default function DetectedRisksList({ risks = [] }) {
  if (!risks.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
      <h3 className="font-semibold text-gray-800 mb-3">
        Detected Risk Factors ({risks.length})
      </h3>
      <ul className="space-y-2">
        {risks.map((risk, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
            <span className="h-2 w-2 rounded-full bg-red-500 flex-shrink-0" />
            {risk}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## src/components/visits/VisitStepIndicator.jsx

```jsx
/**
 * Step progress bar for the 7-step ANC visit form.
 *
 * Props:
 *   currentStep  number (1-7)
 *   steps        string[]  step labels
 */
export default function VisitStepIndicator({ currentStep, steps }) {
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        {steps.map((label, i) => {
          const step = i + 1;
          const done    = step < currentStep;
          const active  = step === currentStep;
          return (
            <div key={i} className="flex flex-col items-center flex-1">
              <div className={`h-8 w-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors
                ${done   ? 'bg-blue-600 border-blue-600 text-white'
                : active ? 'border-blue-600 text-blue-600 bg-white'
                :          'border-gray-300 text-gray-400 bg-white'}`}>
                {done ? '✓' : step}
              </div>
              <span className={`text-xs mt-1 text-center hidden sm:block
                ${active ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
                {label}
              </span>
              {i < steps.length - 1 && (
                <div className={`absolute h-0.5 w-full top-4 left-1/2 -z-10
                  ${done ? 'bg-blue-600' : 'bg-gray-200'}`} />
              )}
            </div>
          );
        })}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1.5">
        <div
          className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }}
        />
      </div>
      <p className="text-sm text-gray-500 mt-1">
        Step {currentStep} of {steps.length}: <span className="font-medium text-gray-700">{steps[currentStep - 1]}</span>
      </p>
    </div>
  );
}
```

---

## src/components/patients/PatientCard.jsx

```jsx
import { useNavigate } from 'react-router-dom';

/**
 * Card shown in the patient list.
 *
 * Props: PatientResponseDTO fields
 */
export default function PatientCard({ patientId, fullName, phone, age, village, district, lmpDate }) {
  const navigate = useNavigate();

  return (
    <div
      className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-blue-300 cursor-pointer transition-all"
      onClick={() => navigate(`/patients/${patientId}`)}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">{fullName}</h3>
          <p className="text-sm text-gray-500 mt-0.5">
            {phone} {age ? `• Age ${age}` : ''} {village ? `• ${village}` : ''}
          </p>
          {district && <p className="text-xs text-gray-400">{district}</p>}
        </div>
        <div className="text-right text-xs text-gray-400">
          {lmpDate && (
            <p>LMP: {new Date(lmpDate).toLocaleDateString('en-IN')}</p>
          )}
          <span className="text-blue-500 font-medium">View →</span>
        </div>
      </div>
    </div>
  );
}
```

---

## src/components/layout/Sidebar.jsx

```jsx
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const navItems = [
  { to: '/dashboard',    label: 'Dashboard',   icon: '📊' },
  { to: '/patients',     label: 'My Patients',  icon: '🤱' },
  { to: '/patients/new', label: 'Add Patient',  icon: '➕' },
];

export default function Sidebar() {
  const { worker, logout } = useAuth();

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Logo / App name */}
      <div className="px-6 py-5 border-b border-gray-100">
        <h1 className="text-lg font-bold text-blue-700">ANC Portal</h1>
        <p className="text-xs text-gray-500 mt-0.5">Maternal Health Risk System</p>
      </div>

      {/* Worker info */}
      {worker && (
        <div className="px-4 py-3 bg-blue-50 border-b border-blue-100">
          <p className="text-sm font-medium text-blue-900">{worker.fullName}</p>
          <p className="text-xs text-blue-600">{worker.healthCenter}</p>
          <p className="text-xs text-blue-500">{worker.district}</p>
        </div>
      )}

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
              ${isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'}`
            }
          >
            <span>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-gray-100">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <span>🚪</span>
          Logout
        </button>
      </div>
    </aside>
  );
}
```

---

## src/components/layout/Topbar.jsx

```jsx
import { useAuth } from '../../hooks/useAuth';

export default function Topbar({ title }) {
  const { worker } = useAuth();
  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <h2 className="text-base font-semibold text-gray-800">{title}</h2>
      {worker && (
        <span className="text-sm text-gray-500">
          {worker.phone}
        </span>
      )}
    </header>
  );
}
```

---

## src/components/layout/AppLayout.jsx

```jsx
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const pageTitles = {
  '/dashboard':    'Dashboard',
  '/patients':     'My Patients',
  '/patients/new': 'Register New Patient',
};

export default function AppLayout() {
  const { pathname } = useLocation();
  const title = pageTitles[pathname] || 'ANC Portal';

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

---

## src/pages/LoginPage.jsx

```jsx
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Login page — calls POST /api/auth/login
 *
 * Form fields: phone, password
 * On success: stores JWT, navigates to /dashboard
 * On failure: displays error from API (e.g. "Invalid phone number or password")
 */
export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [apiError, setApiError]   = useState(null);
  const [loading, setLoading]     = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      await login(data.phone, data.password);
      navigate('/dashboard');
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-md p-8">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-4xl mb-3">🏥</div>
          <h1 className="text-2xl font-bold text-gray-900">ANC Portal</h1>
          <p className="text-gray-500 text-sm mt-1">Maternal Health Risk Assessment</p>
        </div>

        <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField
            label="Phone Number"
            type="tel"
            placeholder="9876543210"
            error={errors.phone?.message}
            {...register('phone', {
              required: 'Phone number is required',
              pattern: {
                value: /^[6-9]\d{9}$/,
                message: 'Enter a valid 10-digit mobile number',
              },
            })}
          />

          <InputField
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'Password must be at least 8 characters' },
            })}
          />

          <Button
            type="submit"
            loading={loading}
            className="w-full mt-2"
          >
            Login
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          New worker?{' '}
          <Link to="/signup" className="text-blue-600 font-medium hover:underline">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/SignupPage.jsx

```jsx
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Signup page — calls POST /api/auth/signup
 *
 * Form fields (match WorkerSignupRequestDTO):
 *   fullName, phone, email, password, healthCenter, district
 *
 * On success: stores JWT, navigates to /dashboard
 */
export default function SignupPage() {
  const { signup }  = useAuth();
  const navigate    = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading]   = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      await signup(data);
      navigate('/dashboard');
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Signup failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-lg p-8">

        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🏥</div>
          <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-500 text-sm">Register as an ANC field worker</p>
        </div>

        <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField
            label="Full Name *"
            placeholder="Anjali Devi"
            error={errors.fullName?.message}
            {...register('fullName', { required: 'Full name is required' })}
          />

          <InputField
            label="Phone Number *"
            type="tel"
            placeholder="9876543210"
            error={errors.phone?.message}
            {...register('phone', {
              required: 'Phone number is required',
              pattern: {
                value: /^[6-9]\d{9}$/,
                message: 'Enter a valid 10-digit mobile number',
              },
            })}
          />

          <InputField
            label="Email Address"
            type="email"
            placeholder="anjali@phc.in"
            error={errors.email?.message}
            {...register('email', {
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Enter a valid email address',
              },
            })}
          />

          <InputField
            label="Password *"
            type="password"
            placeholder="Min. 8 characters"
            error={errors.password?.message}
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'Password must be at least 8 characters' },
            })}
          />

          <InputField
            label="Health Center *"
            placeholder="PHC Angondhalli"
            error={errors.healthCenter?.message}
            {...register('healthCenter', { required: 'Health center is required' })}
          />

          <InputField
            label="District *"
            placeholder="Bangalore Rural"
            error={errors.district?.message}
            {...register('district', { required: 'District is required' })}
          />

          <Button type="submit" loading={loading} className="w-full mt-2">
            Create Account
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-5">
          Already registered?{' '}
          <Link to="/login" className="text-blue-600 font-medium hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/DashboardPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getHighRiskVisits, getCriticalVisits } from '../api/visitApi';
import { getMyPatients } from '../api/patientApi';
import Badge from '../components/ui/Badge';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Dashboard — shows:
 *   - Summary stat cards (patients, high risk, critical)
 *   - Critical visits alert list
 *   - Quick action buttons
 */
export default function DashboardPage() {
  const { worker }   = useAuth();
  const navigate     = useNavigate();
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [stats, setStats]       = useState({ patients: 0, highRisk: 0, critical: 0 });
  const [criticalVisits, setCriticalVisits] = useState([]);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [patients, highRisk, critical] = await Promise.all([
          getMyPatients(),
          getHighRiskVisits(),
          getCriticalVisits(),
        ]);
        setStats({
          patients:  patients.length,
          highRisk:  highRisk.length,
          critical:  critical.length,
        });
        setCriticalVisits(critical.slice(0, 5)); // show top 5
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64"><Spinner size="lg" /></div>
  );

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          Welcome, {worker?.fullName} 👋
        </h2>
        <p className="text-sm text-gray-500">{worker?.healthCenter} • {worker?.district}</p>
      </div>

      <ErrorAlert message={error} />

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard label="My Patients"   value={stats.patients} color="blue"   icon="🤱" />
        <StatCard label="High Risk"     value={stats.highRisk} color="orange"  icon="⚠️" />
        <StatCard label="CRITICAL"      value={stats.critical} color="red"    icon="🚨" />
      </div>

      {/* Quick actions */}
      <div className="flex gap-3 mb-8">
        <button
          onClick={() => navigate('/patients/new')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          ➕ Register New Patient
        </button>
        <button
          onClick={() => navigate('/patients')}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
        >
          📋 View All Patients
        </button>
      </div>

      {/* Critical alerts */}
      {criticalVisits.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <h3 className="font-semibold text-red-800 mb-3 flex items-center gap-2">
            🚨 CRITICAL Cases Requiring Immediate Action
          </h3>
          <div className="space-y-2">
            {criticalVisits.map((visit) => (
              <div
                key={visit.id}
                className="flex items-center justify-between bg-white border border-red-100 rounded-lg p-3 cursor-pointer hover:bg-red-50"
                onClick={() => navigate(`/visits/${visit.id}`)}
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Patient ID: {visit.patientId?.slice(0, 8)}...
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(visit.createdAt).toLocaleString('en-IN')}
                  </p>
                </div>
                <Badge riskLevel={visit.riskLevel} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color, icon }) {
  const colors = {
    blue:   'bg-blue-50 border-blue-200 text-blue-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    red:    'bg-red-50 border-red-200 text-red-700',
  };
  return (
    <div className={`border rounded-xl p-5 ${colors[color]}`}>
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm font-medium mt-1">{label}</div>
    </div>
  );
}
```

---

## src/pages/PatientListPage.jsx

```jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMyPatients } from '../api/patientApi';
import { useApi } from '../hooks/useApi';
import PatientCard from '../components/patients/PatientCard';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Lists all patients registered by the logged-in worker.
 * Each card navigates to /patients/:id
 */
export default function PatientListPage() {
  const navigate = useNavigate();
  const { execute, data: patients, loading, error } = useApi(getMyPatients);

  useEffect(() => { execute(); }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">My Patients</h2>
          <p className="text-sm text-gray-500">{patients?.length || 0} registered</p>
        </div>
        <Button onClick={() => navigate('/patients/new')}>
          ➕ Add Patient
        </Button>
      </div>

      <ErrorAlert message={error} />

      {loading && (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      )}

      {!loading && patients?.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <div className="text-5xl mb-3">🤱</div>
          <p className="font-medium">No patients registered yet</p>
          <p className="text-sm">Click "Add Patient" to register your first patient</p>
        </div>
      )}

      <div className="space-y-3">
        {patients?.map((p) => (
          <PatientCard key={p.patientId} {...p} />
        ))}
      </div>
    </div>
  );
}
```

---

## src/pages/PatientCreatePage.jsx

```jsx
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { createPatient } from '../api/patientApi';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Register a new patient — calls POST /api/patients
 *
 * Form fields match PatientCreateRequestDTO:
 *   fullName, phone, age, address, village, district,
 *   lmpDate, eddDate, bloodGroup
 *
 * workerId is NOT sent — extracted from JWT by Spring Boot.
 *
 * On success: navigate to the new patient's detail page.
 */
export default function PatientCreatePage() {
  const navigate = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading]   = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      const patient = await createPatient(data);
      navigate(`/patients/${patient.patientId}`);
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Failed to register patient. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Register New Patient</h2>
        <p className="text-sm text-gray-500">Enter patient details below</p>
      </div>

      <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
            <InputField
              label="Full Name *"
              placeholder="Meena Kumari"
              error={errors.fullName?.message}
              {...register('fullName', { required: 'Patient name is required' })}
            />
            <InputField
              label="Phone"
              type="tel"
              placeholder="9123456789"
              error={errors.phone?.message}
              {...register('phone')}
            />
            <InputField
              label="Age"
              type="number"
              placeholder="24"
              error={errors.age?.message}
              {...register('age', { valueAsNumber: true })}
            />
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Blood Group</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...register('bloodGroup')}
              >
                <option value="">-- Select --</option>
                {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(bg => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>
            <InputField
              label="Village"
              placeholder="Hebbal"
              {...register('village')}
            />
            <InputField
              label="District"
              placeholder="Bangalore Rural"
              {...register('district')}
            />
            <InputField
              label="LMP Date (Last Menstrual Period)"
              type="date"
              error={errors.lmpDate?.message}
              {...register('lmpDate')}
            />
            <InputField
              label="EDD (Expected Due Date)"
              type="date"
              {...register('eddDate')}
            />
          </div>

          <InputField
            label="Address"
            placeholder="123 Main St, Hebbal"
            {...register('address')}
          />

          <div className="flex gap-3 mt-4">
            <Button type="submit" loading={loading}>
              Register Patient
            </Button>
            <Button variant="secondary" onClick={() => navigate('/patients')}>
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

## src/pages/PatientDetailPage.jsx

```jsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPatientById } from '../api/patientApi';
import { getPatientVisits } from '../api/visitApi';
import { useApi } from '../hooks/useApi';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Shows a patient's profile + their full ANC visit history.
 * Includes a button to start a new ANC visit form.
 */
export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { execute: fetchPatient, data: patient, loading: pLoading, error: pError } = useApi(getPatientById);
  const { execute: fetchVisits, data: visits,  loading: vLoading, error: vError  } = useApi(getPatientVisits);

  useEffect(() => {
    fetchPatient(id);
    fetchVisits(id);
  }, [id]);

  const loading = pLoading || vLoading;

  if (loading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  return (
    <div className="max-w-3xl mx-auto">
      <ErrorAlert message={pError || vError} />

      {/* Patient profile card */}
      {patient && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{patient.fullName}</h2>
              <p className="text-sm text-gray-500">
                {patient.phone}
                {patient.age ? ` • Age ${patient.age}` : ''}
                {patient.bloodGroup ? ` • ${patient.bloodGroup}` : ''}
              </p>
            </div>
            <Button onClick={() => navigate(`/visits/new/${patient.patientId}`)}>
              📋 New ANC Visit
            </Button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
            <InfoItem label="Village"  value={patient.village}   />
            <InfoItem label="District" value={patient.district}  />
            <InfoItem label="LMP Date" value={patient.lmpDate ? new Date(patient.lmpDate).toLocaleDateString('en-IN') : '—'} />
            <InfoItem label="EDD"      value={patient.eddDate ? new Date(patient.eddDate).toLocaleDateString('en-IN') : '—'} />
            <InfoItem label="Address"  value={patient.address}   />
          </div>
        </div>
      )}

      {/* Visit history */}
      <div>
        <h3 className="font-semibold text-gray-800 mb-3">
          ANC Visit History ({visits?.length || 0})
        </h3>

        {visits?.length === 0 && (
          <div className="text-center py-10 text-gray-400 border border-dashed border-gray-200 rounded-xl">
            <p>No visits recorded yet.</p>
            <p className="text-sm">Click "New ANC Visit" to begin.</p>
          </div>
        )}

        <div className="space-y-3">
          {visits?.map((visit) => (
            <div
              key={visit.id}
              className="flex items-center justify-between bg-white border border-gray-200 rounded-xl p-4 cursor-pointer hover:shadow-sm"
              onClick={() => navigate(`/visits/${visit.id}`)}
            >
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Visit — {new Date(visit.createdAt).toLocaleDateString('en-IN')}
                </p>
                <p className="text-xs text-gray-500 mt-0.5">
                  Status: {visit.status}
                  {visit.confidence ? ` • Confidence: ${Math.round(visit.confidence * 100)}%` : ''}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {visit.riskLevel && <Badge riskLevel={visit.riskLevel} />}
                <span className="text-blue-400 text-xs font-medium">View →</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value || '—'}</p>
    </div>
  );
}
```

---

## src/pages/AncVisitFormPage.jsx

```jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { registerVisit } from '../api/visitApi';
import VisitStepIndicator from '../components/visits/VisitStepIndicator';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * 7-step ANC Visit registration form.
 *
 * Each step maps to a DTO section from AncVisitRequestDTO:
 *   Step 1: patient_info       (age, gestationalWeeks)
 *   Step 2: vitals             (heightCm, bmi, bpSystolic, bpDiastolic)
 *   Step 3: lab_reports        (hemoglobin, rhNegative, hivPositive, urineProtein, urineSugar, syphilisPositive)
 *   Step 4: medical_history    (previousLSCS, badObstetricHistory, diabetes, thyroidDisorder, etc.)
 *   Step 5: obstetric_history  (birthOrder, interPregnancyInterval, stillbirthCount, abortionCount)
 *   Step 6: pregnancy_details  (twinPregnancy, malpresentation, placentaPrevia, etc.)
 *   Step 7: current_symptoms   (headache, visualDisturbance, convulsions, etc.)
 *
 * On final step submit: POST /api/anc/register-visit → navigate to /visits/:visitId
 */

const STEPS = [
  'Patient Info',
  'Vitals',
  'Lab Reports',
  'Medical History',
  'Obstetric History',
  'Pregnancy Details',
  'Current Symptoms',
];

export default function AncVisitFormPage() {
  const { patientId } = useParams();
  const navigate      = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData]       = useState({});
  const [submitting, setSubmitting]   = useState(false);
  const [apiError, setApiError]       = useState(null);

  const { register, handleSubmit, formState: { errors }, reset } = useForm();

  const saveStepAndContinue = (stepData) => {
    setFormData((prev) => ({ ...prev, ...stepData }));
    if (currentStep < 7) {
      setCurrentStep((s) => s + 1);
      reset();
    }
  };

  const submitFinalStep = async (stepData) => {
    setApiError(null);
    const allData = { ...formData, ...stepData };
    setSubmitting(true);

    const payload = {
      patientId,
      structured_data: {
        patient_info: {
          age:              Number(allData.age),
          gestationalWeeks: Number(allData.gestationalWeeks),
        },
        vitals: {
          heightCm:   allData.heightCm   ? Number(allData.heightCm)   : null,
          bmi:        allData.bmi        ? Number(allData.bmi)        : null,
          bpSystolic: allData.bpSystolic ? Number(allData.bpSystolic) : null,
          bpDiastolic:allData.bpDiastolic? Number(allData.bpDiastolic): null,
        },
        lab_reports: {
          hemoglobin:       allData.hemoglobin ? Number(allData.hemoglobin) : null,
          rhNegative:       Boolean(allData.rhNegative),
          hivPositive:      Boolean(allData.hivPositive),
          syphilisPositive: Boolean(allData.syphilisPositive),
          urineProtein:     Boolean(allData.urineProtein),
          urineSugar:       Boolean(allData.urineSugar),
        },
        medical_history: {
          previousLSCS:         Boolean(allData.previousLSCS),
          badObstetricHistory:  Boolean(allData.badObstetricHistory),
          previousStillbirth:   Boolean(allData.previousStillbirth),
          previousPretermDelivery: Boolean(allData.previousPretermDelivery),
          previousAbortion:     Boolean(allData.previousAbortion),
          chronicHypertension:  Boolean(allData.chronicHypertension),
          diabetes:             Boolean(allData.diabetes),
          thyroidDisorder:      Boolean(allData.thyroidDisorder),
          smoking:              Boolean(allData.smoking),
          tobaccoUse:           Boolean(allData.tobaccoUse),
          alcoholUse:           Boolean(allData.alcoholUse),
          systemicIllness:      allData.systemicIllness || 'None',
        },
        obstetric_history: {
          birthOrder:             allData.birthOrder             ? Number(allData.birthOrder)             : null,
          interPregnancyInterval: allData.interPregnancyInterval ? Number(allData.interPregnancyInterval) : null,
          stillbirthCount:        allData.stillbirthCount        ? Number(allData.stillbirthCount)        : 0,
          abortionCount:          allData.abortionCount          ? Number(allData.abortionCount)          : 0,
          pretermHistory:         Boolean(allData.pretermHistory),
        },
        pregnancy_details: {
          twinPregnancy:          Boolean(allData.twinPregnancy),
          malpresentation:        Boolean(allData.malpresentation),
          placentaPrevia:         Boolean(allData.placentaPrevia),
          reducedFetalMovement:   Boolean(allData.reducedFetalMovement),
          amnioticFluidNormal:    allData.amnioticFluidNormal !== false,
          umbilicalDopplerAbnormal: Boolean(allData.umbilicalDopplerAbnormal),
        },
        current_symptoms: {
          headache:             Boolean(allData.headache),
          visualDisturbance:    Boolean(allData.visualDisturbance),
          epigastricPain:       Boolean(allData.epigastricPain),
          decreasedUrineOutput: Boolean(allData.decreasedUrineOutput),
          bleedingPerVagina:    Boolean(allData.bleedingPerVagina),
          convulsions:          Boolean(allData.convulsions),
        },
      },
    };

    try {
      const result = await registerVisit(payload);
      navigate(`/visits/${result.visitId}`, { state: { visitData: result } });
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Failed to submit visit. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const onSubmit = currentStep < 7 ? saveStepAndContinue : submitFinalStep;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">New ANC Visit</h2>
        <p className="text-xs text-gray-400">Patient ID: {patientId}</p>
      </div>

      <VisitStepIndicator currentStep={currentStep} steps={STEPS} />
      <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          {/* ── Step 1: Patient Info ─────────────────────────────────── */}
          {currentStep === 1 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Patient Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <InputField
                  label="Age (years) *"
                  type="number"
                  placeholder="28"
                  error={errors.age?.message}
                  {...register('age', {
                    required: 'Age is required',
                    min: { value: 15, message: 'Min age is 15' },
                    max: { value: 55, message: 'Max age is 55' },
                  })}
                />
                <InputField
                  label="Gestational Weeks *"
                  type="number"
                  placeholder="28"
                  error={errors.gestationalWeeks?.message}
                  {...register('gestationalWeeks', {
                    required: 'Gestational weeks required',
                    min: { value: 1,  message: 'Min 1 week' },
                    max: { value: 42, message: 'Max 42 weeks' },
                  })}
                />
              </div>
            </>
          )}

          {/* ── Step 2: Vitals ──────────────────────────────────────── */}
          {currentStep === 2 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Vitals</h3>
              <div className="grid grid-cols-2 gap-4">
                <InputField label="Height (cm)" type="number" placeholder="155" {...register('heightCm')} />
                <InputField label="BMI"         type="number" placeholder="24.5" step="0.1" {...register('bmi')} />
                <InputField label="BP Systolic"  type="number" placeholder="120" {...register('bpSystolic')} />
                <InputField label="BP Diastolic" type="number" placeholder="80"  {...register('bpDiastolic')} />
              </div>
            </>
          )}

          {/* ── Step 3: Lab Reports ─────────────────────────────────── */}
          {currentStep === 3 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Lab Reports</h3>
              <InputField
                label="Hemoglobin (g/dL)"
                type="number"
                placeholder="11.5"
                step="0.1"
                {...register('hemoglobin')}
              />
              <div className="grid grid-cols-2 gap-2">
                {[
                  ['rhNegative',       'Rh Negative'],
                  ['hivPositive',      'HIV Positive'],
                  ['syphilisPositive', 'Syphilis Positive'],
                  ['urineProtein',     'Urine Protein +'],
                  ['urineSugar',       'Urine Sugar +'],
                ].map(([name, label]) => (
                  <CheckboxField key={name} label={label} name={name} register={register} />
                ))}
              </div>
            </>
          )}

          {/* ── Step 4: Medical History ─────────────────────────────── */}
          {currentStep === 4 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Medical History</h3>
              <div className="grid grid-cols-2 gap-2 mb-4">
                {[
                  ['previousLSCS',          'Previous LSCS (C-Section)'],
                  ['badObstetricHistory',    'Bad Obstetric History'],
                  ['previousStillbirth',     'Previous Stillbirth'],
                  ['previousPretermDelivery','Previous Preterm Delivery'],
                  ['previousAbortion',       'Previous Abortion'],
                  ['chronicHypertension',    'Chronic Hypertension'],
                  ['diabetes',               'Diabetes'],
                  ['thyroidDisorder',        'Thyroid Disorder'],
                  ['smoking',                'Smoking'],
                  ['tobaccoUse',             'Tobacco Use'],
                  ['alcoholUse',             'Alcohol Use'],
                ].map(([name, label]) => (
                  <CheckboxField key={name} label={label} name={name} register={register} />
                ))}
              </div>
              <InputField
                label="Systemic Illness (if any)"
                placeholder="e.g. Heart disease, Kidney disease, or None"
                {...register('systemicIllness')}
              />
            </>
          )}

          {/* ── Step 5: Obstetric History ───────────────────────────── */}
          {currentStep === 5 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Obstetric History</h3>
              <div className="grid grid-cols-2 gap-4">
                <InputField
                  label="Birth Order (Gravida)"
                  type="number"
                  placeholder="2"
                  {...register('birthOrder', { valueAsNumber: true })}
                />
                <InputField
                  label="Inter-Pregnancy Interval (months)"
                  type="number"
                  placeholder="24"
                  {...register('interPregnancyInterval', { valueAsNumber: true })}
                />
                <InputField
                  label="Stillbirth Count"
                  type="number"
                  placeholder="0"
                  {...register('stillbirthCount', { valueAsNumber: true })}
                />
                <InputField
                  label="Abortion Count"
                  type="number"
                  placeholder="0"
                  {...register('abortionCount', { valueAsNumber: true })}
                />
              </div>
              <CheckboxField label="Preterm History" name="pretermHistory" register={register} />
            </>
          )}

          {/* ── Step 6: Pregnancy Details ───────────────────────────── */}
          {currentStep === 6 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-4">Current Pregnancy Details</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  ['twinPregnancy',          'Twin / Multiple Pregnancy'],
                  ['malpresentation',        'Malpresentation'],
                  ['placentaPrevia',         'Placenta Previa'],
                  ['reducedFetalMovement',   'Reduced Fetal Movements'],
                  ['umbilicalDopplerAbnormal','Abnormal Umbilical Doppler'],
                ].map(([name, label]) => (
                  <CheckboxField key={name} label={label} name={name} register={register} />
                ))}
                <div className="col-span-2">
                  <label className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="h-4 w-4 rounded border-gray-300 text-blue-600"
                      {...register('amnioticFluidNormal')}
                    />
                    <span className="text-sm text-gray-700">Amniotic Fluid Normal</span>
                  </label>
                </div>
              </div>
            </>
          )}

          {/* ── Step 7: Current Symptoms ────────────────────────────── */}
          {currentStep === 7 && (
            <>
              <h3 className="font-semibold text-gray-700 mb-2">Current Symptoms</h3>
              <p className="text-xs text-gray-400 mb-4">
                ⚠ Mark all symptoms the patient is currently experiencing
              </p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  ['headache',             '🤕 Headache'],
                  ['visualDisturbance',    '👁 Visual Disturbance'],
                  ['epigastricPain',       '🫁 Epigastric Pain'],
                  ['decreasedUrineOutput', '💧 Decreased Urine Output'],
                  ['bleedingPerVagina',    '🩸 Bleeding Per Vagina'],
                  ['convulsions',          '⚡ Convulsions'],
                ].map(([name, label]) => (
                  <CheckboxField key={name} label={label} name={name} register={register} />
                ))}
              </div>
            </>
          )}

          {/* Navigation buttons */}
          <div className="flex gap-3 mt-6 pt-4 border-t border-gray-100">
            {currentStep > 1 && (
              <Button
                variant="secondary"
                type="button"
                onClick={() => { setCurrentStep((s) => s - 1); reset(); }}
              >
                ← Back
              </Button>
            )}
            <Button
              type="submit"
              loading={submitting}
              className="ml-auto"
            >
              {currentStep < 7 ? 'Next →' : '🔍 Analyze Risk'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

/** Reusable checkbox field for the ANC form */
function CheckboxField({ label, name, register }) {
  return (
    <label className="flex items-center gap-2 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors">
      <input
        type="checkbox"
        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        {...register(name)}
      />
      <span className="text-sm text-gray-700">{label}</span>
    </label>
  );
}
```

---

## src/pages/VisitResultPage.jsx

```jsx
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { getVisitById } from '../api/visitApi';
import { useApi } from '../hooks/useApi';
import RiskBanner from '../components/visits/RiskBanner';
import DetectedRisksList from '../components/visits/DetectedRisksList';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

/**
 * Displays the result of a submitted ANC visit.
 *
 * Shows the full FastAPI risk assessment:
 *   - isHighRisk, riskLevel (via RiskBanner)
 *   - detectedRisks[] (via DetectedRisksList)
 *   - explanation (LLM text)
 *   - confidence score
 *   - recommendation
 *
 * Data source: either passed via router state (from AncVisitFormPage)
 * or fetched fresh via GET /api/anc/visits/:visitId
 */
export default function VisitResultPage() {
  const { visitId } = useParams();
  const { state }   = useLocation();
  const navigate    = useNavigate();

  const { execute, data: fetchedVisit, loading, error } = useApi(getVisitById);

  // If navigated directly (not from form), fetch the visit
  useEffect(() => {
    if (!state?.visitData) {
      execute(visitId);
    }
  }, [visitId]);

  // Prefer state data (from form submission), fallback to fetched
  const visitData   = state?.visitData || fetchedVisit;
  const risk        = visitData?.riskAssessment;

  if (loading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  if (error) return (
    <div className="max-w-2xl mx-auto">
      <ErrorAlert message={error} />
      <Button variant="secondary" onClick={() => navigate(-1)}>← Go Back</Button>
    </div>
  );

  if (!visitData) return null;

  return (
    <div className="max-w-2xl mx-auto">

      {/* Back button */}
      <button
        onClick={() => navigate(`/patients/${visitData.patientId}`)}
        className="flex items-center gap-1 text-sm text-blue-600 hover:underline mb-4"
      >
        ← Back to Patient
      </button>

      <h2 className="text-xl font-bold text-gray-900 mb-1">ANC Visit Result</h2>
      <p className="text-xs text-gray-400 mb-4">
        Visit ID: {visitData.visitId} •{' '}
        {visitData.savedAt && new Date(visitData.savedAt).toLocaleString('en-IN')}
      </p>

      {/* Status chip */}
      <div className="flex items-center gap-2 mb-4">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium
          ${visitData.status === 'AI_ANALYZED' ? 'bg-green-100 text-green-700'
          : visitData.status === 'AI_FAILED'   ? 'bg-red-100 text-red-700'
          :                                      'bg-gray-100 text-gray-600'}`}>
          {visitData.status}
        </span>
        {visitData.message && (
          <span className="text-xs text-gray-500">{visitData.message}</span>
        )}
      </div>

      {/* Risk assessment section */}
      {risk ? (
        <>
          {/* Big risk banner */}
          <RiskBanner
            isHighRisk={risk.isHighRisk}
            riskLevel={risk.riskLevel}
            recommendation={risk.recommendation}
          />

          {/* Detected risks list */}
          <DetectedRisksList risks={risk.detectedRisks} />

          {/* Explanation + confidence */}
          {risk.explanation && (
            <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
              <h3 className="font-semibold text-gray-800 mb-2">Clinical Explanation</h3>
              <p className="text-sm text-gray-700 leading-relaxed">{risk.explanation}</p>

              {risk.confidence != null && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                    <span>Model Confidence</span>
                    <span>{Math.round(risk.confidence * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${risk.confidence * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Patient info echoed from FastAPI */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-4">
            <h3 className="font-semibold text-gray-700 mb-2 text-sm">Visit Summary</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-400 text-xs">Age</span>
                <p className="font-medium">{risk.age ?? '—'} years</p>
              </div>
              <div>
                <span className="text-gray-400 text-xs">Gestational Age</span>
                <p className="font-medium">{risk.gestationalWeeks ?? '—'} weeks</p>
              </div>
              <div>
                <span className="text-gray-400 text-xs">Risk Level</span>
                <Badge riskLevel={risk.riskLevel} />
              </div>
              <div>
                <span className="text-gray-400 text-xs">High Risk</span>
                <p className={`font-medium ${risk.isHighRisk ? 'text-red-600' : 'text-green-600'}`}>
                  {risk.isHighRisk ? '⚠ Yes' : '✓ No'}
                </p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 rounded-xl p-4 text-sm">
          ⚠ Risk assessment is not available for this visit.
        </div>
      )}

      {/* Print / action buttons */}
      <div className="flex gap-3 mt-4">
        <Button
          variant="secondary"
          onClick={() => navigate(`/patients/${visitData.patientId}`)}
        >
          ← Patient Profile
        </Button>
        <Button
          variant="secondary"
          onClick={() => window.print()}
        >
          🖨 Print Report
        </Button>
      </div>
    </div>
  );
}
```

---

## src/App.jsx

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';

// Public pages
import LoginPage  from './pages/LoginPage';
import SignupPage from './pages/SignupPage';

// Protected pages
import DashboardPage      from './pages/DashboardPage';
import PatientListPage    from './pages/PatientListPage';
import PatientCreatePage  from './pages/PatientCreatePage';
import PatientDetailPage  from './pages/PatientDetailPage';
import AncVisitFormPage   from './pages/AncVisitFormPage';
import VisitResultPage    from './pages/VisitResultPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes — no JWT needed */}
          <Route path="/login"  element={<LoginPage />}  />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected routes — JWT required, wrapped in AppLayout */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard"          element={<DashboardPage />}     />
              <Route path="/patients"           element={<PatientListPage />}   />
              <Route path="/patients/new"       element={<PatientCreatePage />} />
              <Route path="/patients/:id"       element={<PatientDetailPage />} />
              <Route path="/visits/new/:patientId" element={<AncVisitFormPage />} />
              <Route path="/visits/:visitId"    element={<VisitResultPage />}   />
            </Route>
          </Route>

          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404 fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

---

## src/main.jsx

```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply text-gray-900 antialiased;
  }
}

@layer utilities {
  @media print {
    .no-print { display: none; }
  }
}
```

---

## JWT Token Management — How It All Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      TOKEN LIFECYCLE IN REACT                           │
│                                                                         │
│  1. LOGIN / SIGNUP                                                      │
│     AuthContext.login(phone, password)                                  │
│     → apiLogin() → POST /api/auth/login                                │
│     → receives { token, workerId, fullName, ... }                       │
│     → localStorage.setItem('anc_token', token)       ← stored          │
│     → localStorage.setItem('anc_worker', JSON)        ← stored          │
│     → React state: setToken(), setWorker()            ← in memory       │
│                                                                         │
│  2. EVERY PROTECTED REQUEST                                             │
│     axiosInstance.interceptors.request                                  │
│     → reads localStorage.getItem('anc_token')                           │
│     → sets Authorization: Bearer <token>                                │
│     → Spring Boot JwtAuthFilter validates                               │
│                                                                         │
│  3. APP RELOAD / REFRESH                                                │
│     AuthContext useEffect on mount                                      │
│     → reads localStorage 'anc_token' + 'anc_worker'                    │
│     → restores token + worker state                                     │
│     → user stays logged in across browser refresh                       │
│                                                                         │
│  4. TOKEN EXPIRED (401 response)                                        │
│     axiosInstance.interceptors.response                                 │
│     → catches 401                                                       │
│     → localStorage.removeItem('anc_token')                              │
│     → localStorage.removeItem('anc_worker')                             │
│     → window.location.href = '/login'         ← auto redirect           │
│                                                                         │
│  5. MANUAL LOGOUT                                                       │
│     AuthContext.logout()                                                │
│     → removes localStorage entries                                      │
│     → clears React state                                                │
│     → redirects to /login                                               │
│                                                                         │
│  6. PROTECTED ROUTE GUARD                                               │
│     ProtectedRoute checks isAuthenticated (= !!token in state)          │
│     → if false: <Navigate to="/login" replace />                        │
│     → if true:  render <Outlet /> (the protected page)                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

```bash
# Create project
npm create vite@latest anc-frontend -- --template react
cd anc-frontend

# Install all dependencies
npm install react-router-dom axios react-hook-form date-fns

# Install Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Replace files with the code above, then:
npm run dev
# → http://localhost:5173
```

---

## File Creation Order

```
1.  .env                                  ← VITE_API_BASE_URL
2.  tailwind.config.js + postcss.config.js
3.  src/index.css                         ← @tailwind directives
4.  src/api/axiosInstance.js              ← JWT interceptor (do this first)
5.  src/api/authApi.js
6.  src/api/patientApi.js
7.  src/api/visitApi.js
8.  src/context/AuthContext.jsx           ← login/signup/logout
9.  src/hooks/useAuth.js
10. src/hooks/useApi.js
11. src/routes/ProtectedRoute.jsx
12. src/components/ui/*                   ← Spinner, Button, InputField, Badge, ErrorAlert
13. src/components/layout/*               ← AppLayout, Sidebar, Topbar
14. src/components/patients/PatientCard.jsx
15. src/components/visits/*               ← RiskBanner, DetectedRisksList, VisitStepIndicator
16. src/pages/LoginPage.jsx
17. src/pages/SignupPage.jsx
18. src/pages/DashboardPage.jsx
19. src/pages/PatientListPage.jsx
20. src/pages/PatientCreatePage.jsx
21. src/pages/PatientDetailPage.jsx
22. src/pages/AncVisitFormPage.jsx
23. src/pages/VisitResultPage.jsx
24. src/App.jsx
25. src/main.jsx
```

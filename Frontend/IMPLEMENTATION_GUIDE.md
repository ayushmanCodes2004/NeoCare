# React Frontend Implementation Guide

## ✅ Project Setup Complete

The Vite + React project is already initialized at `Frontend/anc-frontend/`

Dependencies installed:
- ✅ react-router-dom
- ✅ axios  
- ✅ react-hook-form
- ✅ date-fns
- ✅ tailwindcss
- ✅ postcss
- ✅ autoprefixer

## 📦 Next Steps to Complete Implementation

### Step 1: Configure Tailwind CSS

Create `tailwind.config.js`:
```bash
cd Frontend/anc-frontend
npx tailwindcss init -p
```

Or manually create the file with this content:
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

### Step 2: Update index.css

Replace `src/index.css` with:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 3: Create Environment File

Create `.env` in `Frontend/anc-frontend/`:
```
VITE_API_BASE_URL=http://localhost:8080
```

### Step 4: Create Project Structure

Run these commands from `Frontend/anc-frontend/`:

```bash
# Create directory structure
mkdir -p src/api
mkdir -p src/context
mkdir -p src/hooks
mkdir -p src/routes
mkdir -p src/pages
mkdir -p src/components/layout
mkdir -p src/components/ui
mkdir -p src/components/patients
mkdir -p src/components/visits
```

### Step 5: Copy All Source Files

I'll create all the necessary files in the next steps. The complete file list:

**API Layer** (src/api/):
- axiosInstance.js
- authApi.js
- patientApi.js
- visitApi.js

**Context** (src/context/):
- AuthContext.jsx

**Hooks** (src/hooks/):
- useAuth.js
- useApi.js

**Routes** (src/routes/):
- ProtectedRoute.jsx

**Pages** (src/pages/):
- LoginPage.jsx
- SignupPage.jsx
- DashboardPage.jsx
- PatientListPage.jsx
- PatientCreatePage.jsx
- PatientDetailPage.jsx
- AncVisitFormPage.jsx
- VisitResultPage.jsx

**Components - Layout** (src/components/layout/):
- AppLayout.jsx
- Sidebar.jsx
- Topbar.jsx

**Components - UI** (src/components/ui/):
- InputField.jsx
- Button.jsx
- Badge.jsx
- Spinner.jsx
- ErrorAlert.jsx

**Components - Patients** (src/components/patients/):
- PatientCard.jsx

**Components - Visits** (src/components/visits/):
- RiskBanner.jsx
- DetectedRisksList.jsx
- VisitStepIndicator.jsx

**Root Files**:
- src/main.jsx (entry point)
- src/App.jsx (router setup)

## 🚀 Quick Start After Implementation

```bash
cd Frontend/anc-frontend
npm run dev
```

The app will run on `http://localhost:5173`

## 🔗 Backend Integration

Make sure your Spring Boot backend is running on `http://localhost:8080`

The frontend will connect to these endpoints:
- POST /api/auth/signup
- POST /api/auth/login
- GET /api/auth/me
- POST /api/patients
- GET /api/patients
- GET /api/patients/{id}
- POST /api/anc/register-visit
- GET /api/anc/patients/{id}/visits
- GET /api/anc/visits/high-risk
- GET /api/anc/visits/critical

## 📱 Application Flow

1. **Login/Signup** → JWT token stored in localStorage
2. **Dashboard** → Shows summary stats and high-risk alerts
3. **Patient List** → View all patients registered by this worker
4. **Add Patient** → Register new patient
5. **Patient Detail** → View patient info + visit history
6. **ANC Visit Form** → 7-step form to submit visit data
7. **Visit Result** → Shows risk assessment from FastAPI

## 🎨 Features

- ✅ JWT Authentication with auto-refresh
- ✅ Protected routes (redirect to login if not authenticated)
- ✅ Responsive design with Tailwind CSS
- ✅ Form validation with react-hook-form
- ✅ Loading states and error handling
- ✅ Risk level badges (CRITICAL/HIGH/MEDIUM/LOW)
- ✅ Multi-step ANC visit form
- ✅ Patient management
- ✅ Visit history tracking

## 📝 Implementation Status

- ✅ Project initialized
- ✅ Dependencies installed
- ⏳ Tailwind configuration (manual step needed)
- ⏳ Source files creation (in progress)
- ⏳ Testing

## 🔧 Troubleshooting

### Port Already in Use
If port 5173 is busy:
```bash
npm run dev -- --port 3000
```

### CORS Issues
Make sure Spring Boot SecurityConfig allows CORS from `http://localhost:5173`

### API Connection Failed
1. Check Backend is running on port 8080
2. Check `.env` file has correct `VITE_API_BASE_URL`
3. Check browser console for errors

## 📚 Documentation

See `react-frontend.md` for complete specification with all code examples.

---

**Next**: I'll create all the source files systematically.

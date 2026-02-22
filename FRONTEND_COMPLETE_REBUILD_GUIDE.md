# Frontend Complete Rebuild Guide - React2.md Implementation

## Overview
Complete step-by-step guide to rebuild the entire frontend according to react2.md specification.

## Prerequisites

1. **Stop all running processes**
2. **Backup existing frontend** (optional):
   ```bash
   cd Frontend
   mv anc-frontend anc-frontend-backup
   ```
3. **Create fresh frontend**:
   ```bash
   npm create vite@latest anc-frontend -- --template react
   cd anc-frontend
   ```

## Step 1: Clean Installation

```bash
# Remove existing node_modules if any
rm -rf node_modules package-lock.json

# Install base dependencies
npm install
```

## Step 2: Install All Dependencies

```bash
npm install react-router-dom axios react-hook-form recharts lucide-react date-fns sockjs-client @stomp/stompjs clsx

npm install -D tailwindcss postcss autoprefixer

npx tailwindcss init -p
```

## Step 3: Configuration Files

### 1. Update `package.json`
Replace the entire file with:
```json
{
  "name": "anc-portal",
  "version": "2.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "react-hook-form": "^7.51.5",
    "recharts": "^2.12.7",
    "lucide-react": "^0.575.0",
    "date-fns": "^3.6.0",
    "sockjs-client": "^1.6.1",
    "@stomp/stompjs": "^7.0.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.3.1",
    "tailwindcss": "^3.4.4",
    "postcss": "^8.4.39",
    "autoprefixer": "^10.4.19"
  }
}
```

### 2. Create `vite.config.js`
```javascript
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
      '/ws': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        ws: true,
      },
    },
  },
});
```

### 3. Create `tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        display: ['"Syne"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        navy: { 
          950: '#050d1a', 
          900: '#0a1628', 
          800: '#0f2044', 
          700: '#1a3560', 
          600: '#234a80' 
        },
        teal: { 
          400: '#2dd4bf', 
          500: '#14b8a6', 
          600: '#0d9488' 
        },
        risk: {
          critical: '#ef4444',
          high: '#f97316',
          medium: '#eab308',
          low: '#22c55e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: { 
          from: { opacity: 0 }, 
          to: { opacity: 1 } 
        },
        slideUp: { 
          from: { opacity: 0, transform: 'translateY(12px)' }, 
          to: { opacity: 1, transform: 'translateY(0)' } 
        },
      },
    },
  },
  plugins: [],
};
```

### 4. Create `postcss.config.js`
```javascript
export default { 
  plugins: { 
    tailwindcss: {}, 
    autoprefixer: {} 
  } 
};
```

### 5. Create `.env`
```
VITE_API_BASE=http://localhost:8080
```

### 6. Update `index.html`
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

## Step 4: Create Directory Structure

```bash
cd src
mkdir -p api context hooks routes components/{ui,layout,charts,visits,video} pages/{worker,doctor}
```

## Step 5: Core Files

### 1. `src/main.jsx`
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

### 2. `src/index.css`
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
  .risk-high { @apply text-risk-high bg-risk-high/10 border-risk-high/30; }
  .risk-medium { @apply text-risk-medium bg-risk-medium/10 border-risk-medium/30; }
  .risk-low { @apply text-risk-low bg-risk-low/10 border-risk-low/30; }
}
```

## Step 6: API Layer Files

Create all files in `src/api/`:

1. `axiosInstance.js` - Already created ✅
2. `authApi.js` - Worker auth
3. `patientApi.js` - Patient management
4. `visitApi.js` - Visit management
5. `doctorApi.js` - Already created ✅
6. `consultationApi.js` - Already created ✅

## Step 7: Context & Hooks

Create in `src/context/`:
1. `AuthContext.jsx` - Worker auth context
2. `DoctorAuthContext.jsx` - Already created ✅

Create in `src/hooks/`:
1. `useAuth.js` - Worker auth hook
2. `useDoctorAuth.js` - Already created ✅
3. `useApi.js` - Generic API hook

## Step 8: Routing

Create in `src/routes/`:
1. `WorkerRoute.jsx` - Protected worker routes
2. `DoctorRoute.jsx` - Already created ✅

## Step 9: UI Components

Create all in `src/components/ui/`:
1. `Spinner.jsx`
2. `Button.jsx`
3. `Input.jsx`
4. `RiskBadge.jsx`
5. `StatCard.jsx`
6. `Toast.jsx`
7. `Modal.jsx`
8. `EmptyState.jsx`

## Step 10: Layout Components

Create in `src/components/layout/`:
1. `WorkerLayout.jsx`
2. `DoctorLayout.jsx`

## Step 11: Specialized Components

Create in `src/components/`:
- `charts/RiskDonutChart.jsx`
- `visits/StepWizard.jsx`
- `visits/ConfidenceBar.jsx`
- `visits/RiskReport.jsx`
- `video/VideoRoom.jsx` - Update existing with WebRTC

## Step 12: Worker Pages

Create in `src/pages/worker/`:
1. `LoginPage.jsx`
2. `SignupPage.jsx`
3. `DashboardPage.jsx`
4. `PatientListPage.jsx`
5. `PatientCreatePage.jsx`
6. `PatientDetailPage.jsx`
7. `VisitFormPage.jsx`
8. `VisitResultPage.jsx`

## Step 13: Doctor Pages

Create in `src/pages/doctor/`:
1. `DoctorLoginPage.jsx`
2. `DoctorSignupPage.jsx`
3. `DoctorDashboardPage.jsx`
4. `QueuePage.jsx`
5. `ConsultationPage.jsx`
6. `HistoryPage.jsx`

## Step 14: Main App Component

Create `src/App.jsx` with complete routing for both portals.

## Step 15: WebRTC Utility

Update `src/utils/webrtc.js` to use WebSocket signaling.

## Quick Commands Summary

```bash
# 1. Clean start
cd Frontend
rm -rf anc-frontend/node_modules anc-frontend/package-lock.json

# 2. Install dependencies
cd anc-frontend
npm install

# 3. Run development server
npm run dev

# 4. Build for production
npm run build
```

## Troubleshooting

### EBUSY Error
```bash
# Close all terminals and editors
# Then:
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Dependency Conflicts
```bash
npm install --legacy-peer-deps
```

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173
# Or change port in vite.config.js
```

## Testing Checklist

### Worker Portal
- [ ] Worker signup works
- [ ] Worker login works
- [ ] Dashboard displays stats
- [ ] Can create patient
- [ ] Can view patient list
- [ ] Can view patient details
- [ ] Can create ANC visit (7 steps)
- [ ] Visit result shows AI analysis

### Doctor Portal
- [ ] Doctor signup works
- [ ] Doctor login works
- [ ] Dashboard shows queue stats
- [ ] Priority queue displays correctly
- [ ] Can accept consultation
- [ ] Can start WebRTC video call
- [ ] Video streams work (local + remote)
- [ ] Can complete consultation with notes
- [ ] History page shows past consultations

## File Creation Order (Priority)

1. **Critical (Do First)**
   - Configuration files (vite, tailwind, postcss)
   - index.html, main.jsx, index.css
   - API layer (all 6 files)
   - Context (AuthContext, DoctorAuthContext)
   - Hooks (useAuth, useDoctorAuth, useApi)

2. **High Priority**
   - Routes (WorkerRoute, DoctorRoute)
   - UI components (Spinner, Button, Input, RiskBadge)
   - App.jsx with routing

3. **Medium Priority**
   - Layout components
   - Specialized components
   - Doctor pages

4. **Low Priority**
   - Worker pages (if already exist)
   - Charts and visualizations

## Next Steps

Would you like me to:
1. Create all files systematically (will take multiple responses due to size)
2. Create a script to generate all files at once
3. Focus on specific sections first (e.g., doctor portal only)

Let me know your preference and I'll proceed accordingly!

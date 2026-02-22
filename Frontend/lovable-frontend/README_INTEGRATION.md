# 🌸 NeoSure Lovable Frontend

This is the Lovable-generated frontend for the NeoSure Antenatal Care Management System, fully integrated with the Spring Boot backend.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend running on `http://localhost:8080`
- Medical RAG Pipeline running on `http://localhost:8000`

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```
Frontend will be available at: **http://localhost:5173**

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 📡 Backend Connection

### API Base URL
The frontend is configured to connect to your backend at:
```typescript
const API_BASE = 'http://localhost:8080';
```

**File:** `src/services/api.ts`

### Authentication
- JWT tokens stored in `localStorage` with key: `anc_token`
- User role stored with key: `anc_role` ("WORKER" or "DOCTOR")
- User profile stored with key: `anc_user`

### API Endpoints
All backend endpoints are already configured in `src/services/api.ts`:
- Worker auth: `/api/auth/*`
- Doctor auth: `/api/doctor/auth/*`
- Patients: `/api/patients/*`
- ANC Visits: `/api/anc/*`
- Consultations: `/api/consultations/*`

---

## 🗺️ Routes

### Public Routes
- `/` - Landing page
- `/worker/login` - Worker login
- `/worker/signup` - Worker signup
- `/doctor/login` - Doctor login
- `/doctor/signup` - Doctor signup

### Worker Routes (Protected)
- `/worker/dashboard` - Dashboard
- `/worker/patients` - Patient list
- `/worker/patients/new` - Create patient
- `/worker/patients/:id` - Patient details
- `/worker/visits/new` - Register ANC visit
- `/worker/visits/:visitId/result` - AI risk assessment results

### Doctor Routes (Protected)
- `/doctor/dashboard` - Dashboard
- `/doctor/consultations` - Consultation queue
- `/doctor/consultations/:id` - Consultation details
- `/doctor/history` - Consultation history

---

## 🎨 Tech Stack

- **Framework:** React 18.3.1 + TypeScript 5.8.3
- **Build Tool:** Vite 5.4.19
- **Routing:** React Router DOM 6.30.1
- **State Management:** React Context + TanStack React Query 5.83.0
- **Forms:** React Hook Form 7.61.1 + Zod 3.25.76
- **HTTP Client:** Axios 1.13.5
- **UI Components:** ShadCN UI (Radix UI primitives)
- **Styling:** Tailwind CSS 3.4.17
- **Icons:** Lucide React 0.462.0
- **Notifications:** Sonner 1.7.4
- **Date Handling:** date-fns 3.6.0

---

## 📂 Project Structure

```
src/
├── components/          # Reusable components
│   ├── ui/             # ShadCN UI components
│   ├── AppLayout.tsx   # Main layout wrapper
│   ├── ProtectedRoute.tsx  # Route protection
│   └── RiskBadge.tsx   # Risk level badge
│
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
│
├── hooks/              # Custom hooks
│   └── use-toast.ts    # Toast notifications
│
├── lib/                # Utilities
│   └── utils.ts        # Helper functions
│
├── pages/              # Page components
│   ├── Landing.tsx     # Landing page
│   ├── NotFound.tsx    # 404 page
│   ├── worker/         # Worker pages
│   │   ├── WorkerLogin.tsx
│   │   ├── WorkerSignup.tsx
│   │   ├── WorkerDashboard.tsx
│   │   ├── PatientList.tsx
│   │   ├── PatientCreate.tsx
│   │   ├── PatientDetail.tsx
│   │   ├── VisitForm.tsx
│   │   └── VisitResult.tsx
│   └── doctor/         # Doctor pages
│       ├── DoctorLogin.tsx
│       ├── DoctorSignup.tsx
│       ├── DoctorDashboard.tsx
│       ├── ConsultationQueue.tsx
│       ├── ConsultationDetail.tsx
│       └── DoctorHistory.tsx
│
├── services/           # API services
│   └── api.ts          # Axios instance + API functions
│
├── App.tsx             # Main app component
└── main.tsx            # Entry point
```

---

## 🎨 Design System

### Colors
```css
Primary: #C4622D (terracotta orange)
Background: #F5EBE0 (warm beige)
Text: #2C1A0E (dark brown)
Success: #10B981
Warning: #F59E0B
Error: #EF4444
```

### Risk Level Colors
- **LOW**: Green (#10B981)
- **MEDIUM**: Amber (#F59E0B)
- **HIGH**: Orange (#F97316)
- **CRITICAL**: Red (#DC2626)

---

## 🔧 Configuration

### Environment Variables
Create `.env` file (optional):
```env
VITE_API_BASE_URL=http://localhost:8080
```

### Vite Config
**File:** `vite.config.ts`
```typescript
server: {
  host: "::",
  port: 5173,  // Frontend port
}
```

---

## 🧪 Testing

### Run Tests
```bash
npm run test
```

### Watch Mode
```bash
npm run test:watch
```

---

## 🐛 Troubleshooting

### Issue: Can't connect to backend
**Solution:** Ensure backend is running on port 8080
```bash
cd ../../Backend
./run.bat
```

### Issue: Module not found errors
**Solution:** Reinstall dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 5173 already in use
**Solution:** Kill existing process or change port in `vite.config.ts`

---

## 📚 Documentation

- **Integration Guide:** `../../FRONTEND_BACKEND_INTEGRATION.md`
- **API Specification:** `../../LOVABLE_FRONTEND_SPECIFICATION.md`
- **Quick Start:** `../../LOVABLE_QUICK_START.md`
- **Backend API Docs:** http://localhost:8080/swagger-ui/index.html

---

## 🎯 Features Implemented

### ✅ Authentication
- Worker signup/login
- Doctor signup/login
- JWT token management
- Auto-logout on 401
- Protected routes

### ✅ Worker Features
- Dashboard with statistics
- Patient list with search
- Create new patient
- View patient details
- Register ANC visit (multi-step form)
- View AI risk assessment results
- Visit history per patient

### ✅ Doctor Features
- Dashboard with queue preview
- Priority consultation queue
- Filter by status
- View consultation details
- Accept consultation
- Complete consultation with notes
- Consultation history

### ✅ UI/UX
- Responsive design
- Toast notifications
- Loading states
- Error handling
- Form validation
- Risk level badges
- Clean, professional design

---

## 🚀 Deployment

### Build
```bash
npm run build
```

Output will be in `dist/` directory.

### Deploy to Vercel/Netlify
1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable: `VITE_API_BASE_URL=<your-backend-url>`

---

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode

---

## 🤝 Contributing

This frontend was generated by Lovable and integrated with the NeoSure backend. For backend changes, see `../../Backend/README.md`.

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using Lovable**

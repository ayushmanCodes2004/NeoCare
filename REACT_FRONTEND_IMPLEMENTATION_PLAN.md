# React Frontend Implementation Plan - Doctor Module

## Overview
Complete React frontend implementation for the doctor module based on react2.md specification (3279 lines).

## Implementation Status

### ✅ Already Completed (From Previous Work)
1. `Frontend/anc-frontend/src/utils/webrtc.js` - WebRTC manager
2. `Frontend/anc-frontend/src/pages/VideoConsultationPage.jsx` - Video call UI
3. `Frontend/anc-frontend/src/pages/ConsultationDetailPage.jsx` - Consultation details
4. `Frontend/anc-frontend/src/pages/ConsultationListPage.jsx` - Consultation list
5. `Frontend/anc-frontend/src/pages/DoctorDashboardPage.jsx` - Doctor dashboard
6. `Frontend/anc-frontend/src/pages/DoctorSignupPage.jsx` - Doctor signup
7. `Frontend/anc-frontend/src/pages/DoctorLoginPage.jsx` - Doctor login

### 📦 Package.json Updated
- ✅ Added all required dependencies
- ✅ Includes WebRTC dependencies (sockjs-client, @stomp/stompjs)
- ✅ Removed @daily-co/daily-js (using WebRTC instead)

## Files to Create (Priority Order)

### Phase 1: Core Infrastructure (High Priority)
1. **API Layer**
   - `src/api/axiosInstance.js` - Axios configuration with JWT interceptor
   - `src/api/doctorApi.js` - Doctor authentication APIs
   - `src/api/consultationApi.js` - Consultation management APIs
   - `src/api/authApi.js` - Worker authentication APIs
   - `src/api/patientApi.js` - Patient management APIs
   - `src/api/visitApi.js` - Visit management APIs

2. **Context & Auth**
   - `src/context/DoctorAuthContext.jsx` - Doctor authentication context
   - `src/context/AuthContext.jsx` - Worker authentication context
   - `src/hooks/useDoctorAuth.js` - Doctor auth hook
   - `src/hooks/useAuth.js` - Worker auth hook
   - `src/hooks/useApi.js` - Generic API hook

3. **Routing**
   - `src/routes/DoctorRoute.jsx` - Protected doctor routes
   - `src/routes/WorkerRoute.jsx` - Protected worker routes
   - `src/App.jsx` - Main app with routing

### Phase 2: UI Components (Medium Priority)
4. **Base UI Components**
   - `src/components/ui/Button.jsx` - Button component
   - `src/components/ui/Input.jsx` - Input component
   - `src/components/ui/Spinner.jsx` - Loading spinner
   - `src/components/ui/RiskBadge.jsx` - Risk level badge
   - `src/components/ui/StatCard.jsx` - Statistics card
   - `src/components/ui/Toast.jsx` - Toast notifications
   - `src/components/ui/Modal.jsx` - Modal dialog
   - `src/components/ui/EmptyState.jsx` - Empty state component

5. **Layout Components**
   - `src/components/layout/DoctorLayout.jsx` - Doctor portal layout
   - `src/components/layout/WorkerLayout.jsx` - Worker portal layout

6. **Specialized Components**
   - `src/components/charts/RiskDonutChart.jsx` - Risk distribution chart
   - `src/components/visits/StepWizard.jsx` - Multi-step form wizard
   - `src/components/visits/ConfidenceBar.jsx` - AI confidence bar
   - `src/components/visits/RiskReport.jsx` - Risk assessment report
   - `src/components/video/VideoRoom.jsx` - Video call room (update existing)

### Phase 3: Configuration (High Priority)
7. **Build Configuration**
   - `vite.config.js` - Vite configuration with proxy
   - `tailwind.config.js` - Tailwind CSS configuration
   - `postcss.config.js` - PostCSS configuration
   - `.env` - Environment variables
   - `index.html` - HTML template
   - `src/index.css` - Global styles
   - `src/main.jsx` - React entry point

### Phase 4: Worker Portal Pages (Low Priority - Already Exists)
8. **Worker Pages** (Most already exist, may need updates)
   - `src/pages/worker/LoginPage.jsx`
   - `src/pages/worker/SignupPage.jsx`
   - `src/pages/worker/DashboardPage.jsx`
   - `src/pages/worker/PatientListPage.jsx`
   - `src/pages/worker/PatientCreatePage.jsx`
   - `src/pages/worker/PatientDetailPage.jsx`
   - `src/pages/worker/VisitFormPage.jsx`
   - `src/pages/worker/VisitResultPage.jsx`

### Phase 5: Doctor Portal Pages (Already Completed)
9. **Doctor Pages** ✅
   - `src/pages/doctor/DoctorLoginPage.jsx` ✅
   - `src/pages/doctor/DoctorSignupPage.jsx` ✅
   - `src/pages/doctor/DoctorDashboardPage.jsx` ✅
   - `src/pages/doctor/QueuePage.jsx` (ConsultationListPage.jsx) ✅
   - `src/pages/doctor/ConsultationPage.jsx` (ConsultationDetailPage.jsx) ✅
   - `src/pages/doctor/HistoryPage.jsx` (needs creation)
   - `src/pages/doctor/VideoCallPage.jsx` (VideoConsultationPage.jsx) ✅

## Implementation Strategy

### Immediate Actions (Next Steps)
1. ✅ Update package.json with all dependencies
2. Create core infrastructure files (API, Context, Hooks)
3. Create routing and App.jsx
4. Create UI components
5. Create configuration files
6. Test doctor portal flow
7. Update/create missing pages

### Testing Checklist
- [ ] Doctor signup works
- [ ] Doctor login works
- [ ] Priority queue displays correctly
- [ ] Doctor can accept consultation
- [ ] WebRTC video call works
- [ ] Doctor can complete consultation with notes
- [ ] Consultation history displays
- [ ] Worker can view patient consultations

## Key Features to Implement

### Doctor Portal
1. **Authentication**
   - Signup with phone, email, password, hospital, district
   - Login with phone and password
   - JWT token storage and management
   - Role-based routing (DOCTOR role)

2. **Priority Queue**
   - Display consultations sorted by priority (CRITICAL → HIGH → MEDIUM)
   - Show patient info, risk level, gestational weeks
   - Accept consultation button
   - Real-time updates

3. **Consultation Detail**
   - Full patient information
   - Visit data with AI analysis
   - Detected risks and explanation
   - Worker information
   - Start video call button
   - Complete consultation form

4. **Video Consultation**
   - WebRTC peer-to-peer video
   - Local and remote video streams
   - Video/audio toggle controls
   - Connection status indicator
   - End call button

5. **Consultation Completion**
   - Doctor notes textarea
   - Diagnosis field
   - Action plan textarea
   - Submit button
   - Status update to COMPLETED

6. **History**
   - List of past consultations
   - Filter by status
   - View details
   - Search functionality

### WebRTC Integration
- Uses existing `src/utils/webrtc.js`
- STOMP WebSocket signaling at `ws://localhost:8080/ws/consultation`
- Peer-to-peer video/audio streaming
- ICE candidate exchange
- Connection state monitoring

## Design System

### Colors
- **Navy**: Background (#050d1a, #0a1628, #0f2044)
- **Teal**: Primary accent (#14b8a6, #2dd4bf)
- **Risk Colors**:
  - Critical: #ef4444 (red)
  - High: #f97316 (orange)
  - Medium: #eab308 (yellow)
  - Low: #22c55e (green)

### Typography
- **Display**: Syne (headings)
- **Body**: DM Sans (text)
- **Mono**: JetBrains Mono (labels, code)

### Components Style
- Glass morphism effects
- Rounded corners (rounded-2xl)
- Subtle borders (border-white/10)
- Smooth animations
- Medical-grade precision

## API Endpoints Used

### Doctor Authentication
- `POST /api/doctor/auth/signup`
- `POST /api/doctor/auth/login`
- `GET /api/doctor/auth/me`

### Consultation Management
- `GET /api/consultations/queue`
- `GET /api/consultations/:id`
- `POST /api/consultations/:id/accept`
- `POST /api/consultations/:id/start-call`
- `POST /api/consultations/:id/complete`
- `GET /api/consultations/my-history`
- `GET /api/consultations/patient/:patientId`

### WebSocket
- `ws://localhost:8080/ws/consultation`
- `/topic/consultation/:id` (subscribe)
- `/app/consultation/:id/signal` (send)
- `/app/consultation/:id/join` (send)
- `/app/consultation/:id/leave` (send)

## File Size Estimates
- Total files to create: ~40 files
- Estimated total lines: ~5000 lines
- Implementation time: 6-8 hours

## Dependencies Installation
```bash
cd Frontend/anc-frontend
npm install
```

## Running the Application
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Next Steps
1. Create API layer files (axiosInstance, doctorApi, consultationApi)
2. Create context and hooks (DoctorAuthContext, useDoctorAuth)
3. Create routing (DoctorRoute, App.jsx)
4. Create UI components (Button, Input, RiskBadge, etc.)
5. Create configuration files (vite.config.js, tailwind.config.js)
6. Test complete flow

---

**Status**: Package.json updated, implementation plan complete
**Priority**: Create core infrastructure files first
**Estimated Completion**: 6-8 hours for full implementation

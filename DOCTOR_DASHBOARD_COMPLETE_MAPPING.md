# Doctor Dashboard - Complete Backend-Frontend Mapping

## Overview
This document maps all backend APIs to frontend components for the doctor dashboard system.

---

## 1. AUTHENTICATION FLOW

### Backend APIs

#### Doctor Signup
- **Endpoint**: `POST /api/auth/doctor/signup`
- **Controller**: `DoctorAuthController.signup()`
- **Service**: `DoctorAuthService.signup()`
- **Request Body**:
```json
{
  "fullName": "Dr. Priya Sharma",
  "email": "priya@hospital.com",
  "phone": "9876543210",
  "password": "password123",
  "specialization": "Gynecologist",
  "licenseNumber": "MCI-12345",
  "hospital": "City General Hospital",
  "district": "Bangalore Urban",
  "yearsOfExperience": 5
}
```
- **Response**:
```json
{
  "token": "jwt-token-here",
  "workerId": "uuid",
  "fullName": "Dr. Priya Sharma",
  "email": "priya@hospital.com",
  "phone": "9876543210",
  "healthCenter": "City General Hospital",
  "district": "Bangalore Urban",
  "message": "Doctor registered successfully"
}
```

#### Doctor Login
- **Endpoint**: `POST /api/auth/doctor/login`
- **Controller**: `DoctorAuthController.login()`
- **Service**: `DoctorAuthService.login()`
- **Request Body**:
```json
{
  "phone": "priya@hospital.com",  // Email sent in phone field
  "password": "password123"
}
```
- **Response**: Same as signup

#### Get Doctor Profile
- **Endpoint**: `GET /api/auth/doctor/me`
- **Controller**: `DoctorAuthController.getProfile()`
- **Service**: `DoctorAuthService.getDoctorProfile()`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
  "doctorId": "uuid",
  "fullName": "Dr. Priya Sharma",
  "email": "priya@hospital.com",
  "phone": "9876543210",
  "specialization": "Gynecologist",
  "licenseNumber": "MCI-12345",
  "hospital": "City General Hospital",
  "district": "Bangalore Urban",
  "yearsOfExperience": 5,
  "isAvailable": true,
  "role": "DOCTOR"
}
```

### Frontend Components

#### DoctorSignupPage.jsx
- **Route**: `/doctor/signup`
- **API Call**: `POST /api/auth/doctor/signup`
- **On Success**:
  - Stores: `token`, `userRole: 'DOCTOR'`, `doctorId`, `doctorInfo`
  - Redirects: `window.location.href = '/doctor/dashboard'`

#### DoctorLoginPage.jsx
- **Route**: `/doctor/login`
- **API Calls**:
  1. `POST /api/auth/doctor/login`
  2. `GET /api/auth/doctor/me` (to get specialization)
- **On Success**:
  - Stores: `token`, `userRole: 'DOCTOR'`, `doctorId`, `doctorInfo`
  - Redirects: `window.location.href = '/doctor/dashboard'`

---

## 2. DOCTOR DASHBOARD

### Backend APIs

#### Get Pending Consultations
- **Endpoint**: `GET /api/consultations/pending`
- **Controller**: `ConsultationController.getPendingRequests()`
- **Service**: `ConsultationService.getPendingRequests()`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
[
  {
    "consultationId": "uuid",
    "patientId": "uuid",
    "patientName": "Anita Sharma",
    "patientRchId": "RCH123456",
    "patientAge": 28,
    "gestationWeeks": 32,
    "gestationDays": 4,
    "riskLevel": "HIGH",
    "reasonForConsultation": "High blood pressure detected",
    "status": "PENDING",
    "visitId": "visit-uuid",
    "createdAt": "2026-02-22T10:30:00"
  }
]
```

#### Get Patient Visit Report
- **Endpoint**: `GET /api/anc/visits/{visitId}`
- **Controller**: `AncVisitController.getVisit()`
- **Service**: `AncVisitService.getVisitById()`
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
  "visitId": "visit-uuid",
  "patientId": "uuid",
  "systolicBp": 140,
  "diastolicBp": 90,
  "weight": 65.5,
  "hemoglobin": 10.5,
  "bloodSugar": 95,
  "symptoms": ["Headache", "Swelling in feet"],
  "riskLevel": "HIGH",
  "riskFactors": ["Hypertension", "Low hemoglobin"],
  "recommendations": "Immediate consultation required. Monitor BP closely."
}
```

#### Accept Consultation
- **Endpoint**: `PUT /api/consultations/{id}/accept`
- **Controller**: `ConsultationController.acceptConsultation()`
- **Service**: `ConsultationService.acceptConsultation()`
- **Headers**: `Authorization: Bearer {token}`
- **Response**: Updated consultation object

#### Start Video Consultation
- **Endpoint**: `PUT /api/consultations/{id}/start`
- **Controller**: `ConsultationController.startConsultation()`
- **Service**: `ConsultationService.startConsultation()`
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
```json
{
  "roomId": "room-uuid"
}
```

### Frontend Component

#### DoctorDashboardPage.jsx
- **Route**: `/doctor/dashboard`
- **Protected**: Yes (requires `token` and `userRole: 'DOCTOR'`)

**Data Flow**:

1. **On Mount** (`useEffect`):
   ```javascript
   - Fetch doctorInfo from localStorage
   - Call GET /api/consultations/pending
   - Sort consultations by risk: CRITICAL > HIGH > MODERATE > LOW
   - Display in patient queue
   ```

2. **View Report Button** (`handleViewReport`):
   ```javascript
   - Call GET /api/anc/visits/{visitId}
   - Display patient report in sidebar panel
   - Show: vitals, symptoms, risk assessment, recommendations
   ```

3. **Start Video Call Button** (`handleStartConsultation`):
   ```javascript
   - Call PUT /api/consultations/{id}/accept
   - Navigate to /doctor/video-consultation/{id}
   ```

**UI Sections**:
- Welcome header with Namaste greeting
- Priority stats cards (Critical, High Risk, Total Pending)
- Patient queue list (sorted by risk)
- Patient report panel (sticky sidebar)

---

## 3. SECURITY CONFIGURATION

### Backend - SecurityConfig.java

**Permitted Endpoints** (no authentication required):
```java
.requestMatchers("/api/auth/signup", "/api/auth/login").permitAll()
.requestMatchers("/api/auth/doctor/signup", "/api/auth/doctor/login").permitAll()
.requestMatchers("/ws/**").permitAll()
```

**Protected Endpoints**:
```java
.requestMatchers("/api/doctor/**").hasRole("DOCTOR")
.requestMatchers("/api/consultations/**").hasAnyRole("WORKER", "DOCTOR")
```

### Frontend - Route Protection

**ProtectedRoute.jsx**:
- Checks `isAuthenticated` from AuthContext
- Redirects to `/login` if not authenticated

**DashboardPage.jsx**:
- Checks `userRole === 'DOCTOR'`
- Redirects doctors to `/doctor/dashboard`

---

## 4. DATA STORAGE

### LocalStorage Keys

**After Doctor Login/Signup**:
```javascript
{
  "token": "jwt-token",
  "userRole": "DOCTOR",
  "doctorId": "uuid",
  "doctorInfo": {
    "fullName": "Dr. Priya Sharma",
    "email": "priya@hospital.com",
    "phone": "9876543210",
    "specialization": "Gynecologist",
    "hospital": "City General Hospital",
    "district": "Bangalore Urban"
  }
}
```

---

## 5. COMPLETE API MAPPING TABLE

| Frontend Action | HTTP Method | Backend Endpoint | Controller Method | Service Method |
|----------------|-------------|------------------|-------------------|----------------|
| Doctor Signup | POST | `/api/auth/doctor/signup` | `DoctorAuthController.signup()` | `DoctorAuthService.signup()` |
| Doctor Login | POST | `/api/auth/doctor/login` | `DoctorAuthController.login()` | `DoctorAuthService.login()` |
| Get Profile | GET | `/api/auth/doctor/me` | `DoctorAuthController.getProfile()` | `DoctorAuthService.getDoctorProfile()` |
| Get Pending Consultations | GET | `/api/consultations/pending` | `ConsultationController.getPendingRequests()` | `ConsultationService.getPendingRequests()` |
| Get Patient Report | GET | `/api/anc/visits/{visitId}` | `AncVisitController.getVisit()` | `AncVisitService.getVisitById()` |
| Accept Consultation | PUT | `/api/consultations/{id}/accept` | `ConsultationController.acceptConsultation()` | `ConsultationService.acceptConsultation()` |
| Start Video Call | PUT | `/api/consultations/{id}/start` | `ConsultationController.startConsultation()` | `ConsultationService.startConsultation()` |

---

## 6. TESTING CHECKLIST

### Backend
- [ ] Compile: `mvn clean compile`
- [ ] Run: `mvn spring-boot:run`
- [ ] Verify running on: `http://localhost:8080`
- [ ] Check database tables exist: `doctors`, `consultations`

### Frontend
- [ ] Install dependencies: `npm install`
- [ ] Run: `npm run dev`
- [ ] Verify running on: `http://localhost:5174`

### Integration Test Flow
1. [ ] Navigate to `http://localhost:5174/doctor/signup`
2. [ ] Fill signup form and submit
3. [ ] Verify redirect to `/doctor/dashboard`
4. [ ] Check browser console for stored data
5. [ ] Verify "DOCTOR PORTAL" appears in topbar
6. [ ] Check dashboard shows Namaste greeting
7. [ ] Verify priority stats cards display
8. [ ] Check patient queue (may be empty if no consultations)
9. [ ] Logout and login again at `/doctor/login`
10. [ ] Verify redirect to `/doctor/dashboard` again

---

## 7. TROUBLESHOOTING

### Issue: Login fails with 401
- **Check**: Doctor exists in database
- **Check**: Password is correct
- **Check**: Backend is running
- **Solution**: Sign up first, then login

### Issue: Redirects to worker dashboard
- **Check**: `userRole` in localStorage is `'DOCTOR'`
- **Check**: Using `/doctor/login` not `/login`
- **Solution**: Clear localStorage and login again

### Issue: Dashboard shows no consultations
- **Check**: Consultations exist in database
- **Check**: API call succeeds (check Network tab)
- **Solution**: Create test consultation via worker portal

### Issue: Cannot view patient report
- **Check**: Visit exists in database
- **Check**: `visitId` is correct in consultation
- **Solution**: Ensure ANC visit was created for patient

---

## 8. FILE LOCATIONS

### Backend Files
```
Backend/
├── src/main/java/com/anc/
│   ├── controller/
│   │   ├── DoctorAuthController.java
│   │   ├── ConsultationController.java
│   │   └── AncVisitController.java
│   ├── service/
│   │   ├── DoctorAuthService.java
│   │   ├── ConsultationService.java
│   │   └── AncVisitService.java
│   ├── entity/
│   │   └── DoctorEntity.java
│   ├── repository/
│   │   └── DoctorRepository.java
│   └── security/
│       └── SecurityConfig.java
└── src/main/resources/
    └── doctor_consultation_schema.sql
```

### Frontend Files
```
Frontend/anc-frontend/src/
├── pages/
│   ├── DoctorLoginPage.jsx
│   ├── DoctorSignupPage.jsx
│   └── DoctorDashboardPage.jsx
├── context/
│   └── AuthContext.jsx
├── routes/
│   └── ProtectedRoute.jsx
├── components/layout/
│   └── Topbar.jsx
├── styles/
│   └── dashboard.css
└── App.jsx
```

---

## SUMMARY

✅ **Backend**: All APIs properly configured with JWT authentication
✅ **Frontend**: Doctor dashboard with beautiful NeoSure design
✅ **Security**: Role-based access control (DOCTOR vs WORKER)
✅ **Routing**: Proper redirects based on user role
✅ **Data Flow**: Complete mapping from API to UI components
✅ **Styling**: Terra color scheme with Cormorant Garamond fonts

The doctor dashboard is fully integrated and ready to use!

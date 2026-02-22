# API Mapping Fixes Applied

## ✅ All Critical Issues Fixed

### 1. Doctor Login Endpoint ✅
**Before:** `/api/auth/doctor/login`  
**After:** `/api/doctor/auth/login`  
**File:** `Frontend/anc-frontend/src/pages/DoctorLoginPage.jsx`

### 2. Doctor Profile Endpoint ✅
**Before:** `/api/auth/doctor/me`  
**After:** `/api/doctor/auth/me`  
**File:** `Frontend/anc-frontend/src/pages/DoctorLoginPage.jsx`

### 3. Consultations Queue Endpoint ✅
**Before:** `/api/consultations/pending`  
**After:** `/api/consultations/queue`  
**File:** `Frontend/anc-frontend/src/pages/DoctorDashboardPage.jsx`

### 4. Doctor History Endpoint ✅
**Before:** `/api/consultations/doctor/my-consultations`  
**After:** `/api/consultations/my-history`  
**File:** `Frontend/anc-frontend/src/pages/ConsultationListPage.jsx`

### 5. Consultation Accept Method ✅
**Before:** `PUT /api/consultations/:id/accept`  
**After:** `POST /api/consultations/:id/accept`  
**File:** `Frontend/anc-frontend/src/pages/DoctorDashboardPage.jsx`

### 6. Consultation Complete Method ✅
**Before:** `PUT /api/consultations/:id/complete`  
**After:** `POST /api/consultations/:id/complete`  
**File:** `Frontend/anc-frontend/src/pages/ConsultationDetailPage.jsx`

### 7. Consultation Schedule Endpoint ⚠️
**Status:** Added warning comment - backend endpoint not implemented  
**File:** `Frontend/anc-frontend/src/pages/ConsultationDetailPage.jsx`  
**Note:** Changed from PUT to POST, added console warning

### 8. Token Storage Standardization ✅
**Before:** Mixed usage of `token`, `userRole`, `doctorId`, `doctorInfo`  
**After:** Standardized to `anc_token`, `anc_role`, `anc_user`  
**Files Fixed:**
- `Frontend/anc-frontend/src/pages/DoctorLoginPage.jsx`
- `Frontend/anc-frontend/src/pages/DoctorSignupPage.jsx`
- `Frontend/anc-frontend/src/pages/DoctorDashboardPage.jsx`
- `Frontend/anc-frontend/src/pages/ConsultationListPage.jsx`
- `Frontend/anc-frontend/src/pages/ConsultationDetailPage.jsx`
- `Frontend/anc-frontend/src/pages/VideoConsultationPage.jsx`

---

## 📊 Complete API Mapping (After Fixes)

### Worker Authentication
| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| Signup | POST | `/api/auth/signup` | `/api/auth/signup` | ✅ |
| Login | POST | `/api/auth/login` | `/api/auth/login` | ✅ |
| Profile | GET | `/api/auth/me` | `/api/auth/me` | ✅ |

### Doctor Authentication
| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| Signup | POST | `/api/doctor/auth/signup` | `/api/doctor/auth/signup` | ✅ |
| Login | POST | `/api/doctor/auth/login` | `/api/doctor/auth/login` | ✅ |
| Profile | GET | `/api/doctor/auth/me` | `/api/doctor/auth/me` | ✅ |

### Patient Management
| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| Create | POST | `/api/patients` | `/api/patients` | ✅ |
| List | GET | `/api/patients` | `/api/patients` | ✅ |
| Get One | GET | `/api/patients/:id` | `/api/patients/:id` | ✅ |

### ANC Visits
| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| Register | POST | `/api/anc/register-visit` | `/api/anc/register-visit` | ✅ |
| Get Visit | GET | `/api/anc/visits/:id` | `/api/anc/visits/:id` | ✅ |
| Patient Visits | GET | `/api/anc/patients/:id/visits` | `/api/anc/patients/:id/visits` | ✅ |
| High Risk | GET | `/api/anc/visits/high-risk` | `/api/anc/visits/high-risk` | ✅ |
| Critical | GET | `/api/anc/visits/critical` | `/api/anc/visits/critical` | ✅ |

### Consultations
| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| Queue | GET | `/api/consultations/queue` | `/api/consultations/queue` | ✅ |
| Get One | GET | `/api/consultations/:id` | `/api/consultations/:id` | ✅ |
| Accept | POST | `/api/consultations/:id/accept` | `/api/consultations/:id/accept` | ✅ |
| Start Call | POST | `/api/consultations/:id/start-call` | `/api/consultations/:id/start-call` | ✅ |
| Complete | POST | `/api/consultations/:id/complete` | `/api/consultations/:id/complete` | ✅ |
| History | GET | `/api/consultations/my-history` | `/api/consultations/my-history` | ✅ |
| Patient Consults | GET | `/api/consultations/patient/:id` | `/api/consultations/patient/:id` | ✅ |
| Schedule | POST | `/api/consultations/:id/schedule` | ❌ NOT IMPLEMENTED | ⚠️ |

---

## 🔐 Security Configuration

All endpoints properly configured in `SecurityConfig.java`:

### Public Endpoints
- `/api/auth/signup`
- `/api/auth/login`
- `/api/doctor/auth/signup`
- `/api/doctor/auth/login`
- `/ws/**` (WebSocket)

### Doctor-Only Endpoints (ROLE_DOCTOR)
- `/api/doctor/auth/me`
- `/api/consultations/queue`
- `/api/consultations/my-history`
- `/api/consultations/*/accept`
- `/api/consultations/*/start-call`
- `/api/consultations/*/complete`

### Authenticated Endpoints (Both Roles)
- `/api/consultations/**` (other consultation endpoints)
- All other endpoints require valid JWT

---

## 📝 LocalStorage Keys Standardized

### Before (Inconsistent)
```javascript
localStorage.getItem('token')
localStorage.getItem('userRole')
localStorage.getItem('doctorId')
localStorage.getItem('doctorInfo')
```

### After (Consistent)
```javascript
localStorage.getItem('anc_token')    // JWT token
localStorage.getItem('anc_role')     // 'WORKER' or 'DOCTOR'
localStorage.getItem('anc_user')     // JSON string with user info
```

This matches the implementation in:
- `AuthContext.jsx`
- `DoctorAuthContext.jsx`
- `axiosInstance.js`

---

## ⚠️ Known Issues

### 1. Schedule Endpoint Not Implemented
**Frontend:** Calls `POST /api/consultations/:id/schedule`  
**Backend:** Endpoint does not exist  
**Impact:** Schedule functionality will fail  
**Recommendation:** Either implement backend endpoint or remove frontend feature

### 2. Response Field Mapping
Some response fields may need verification:
- Doctor signup/login returns `doctorId` (verify field name)
- Worker signup/login returns `workerId` (verify field name)
- Hospital field: backend uses `hospital`, frontend may expect `healthCenter`

---

## 🎯 Testing Checklist

### Worker Flow
- [ ] Worker signup
- [ ] Worker login
- [ ] Create patient
- [ ] List patients
- [ ] View patient details
- [ ] Register ANC visit
- [ ] View visit results

### Doctor Flow
- [ ] Doctor signup ✅ (fixed)
- [ ] Doctor login ✅ (fixed)
- [ ] View consultation queue ✅ (fixed)
- [ ] Accept consultation ✅ (fixed)
- [ ] Start video call
- [ ] Complete consultation ✅ (fixed)
- [ ] View consultation history ✅ (fixed)

---

## 🚀 Next Steps

1. Test doctor signup/login flow
2. Verify all consultation endpoints work
3. Test token persistence across page refreshes
4. Decide on schedule endpoint (implement or remove)
5. Verify response field mappings match DTOs

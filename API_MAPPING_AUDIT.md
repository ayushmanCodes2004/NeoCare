# API Mapping Audit - Frontend ↔ Backend

## 🔴 CRITICAL ISSUES FOUND

### 1. Doctor Login Endpoint Mismatch
**Frontend (DoctorLoginPage.jsx):**
```javascript
axios.post(`${API_BASE_URL}/api/auth/doctor/login`, {...})
```

**Backend (DoctorAuthController.java):**
```java
@PostMapping("/login")  // Under @RequestMapping("/api/doctor/auth")
// Actual endpoint: /api/doctor/auth/login
```

**❌ MISMATCH:** Frontend calls `/api/auth/doctor/login` but backend expects `/api/doctor/auth/login`

---

### 2. Doctor Profile Endpoint Mismatch
**Frontend (DoctorLoginPage.jsx):**
```javascript
axios.get(`${API_BASE_URL}/api/auth/doctor/me`, {...})
```

**Backend (DoctorAuthController.java):**
```java
@GetMapping("/me")  // Under @RequestMapping("/api/doctor/auth")
// Actual endpoint: /api/doctor/auth/me
```

**❌ MISMATCH:** Frontend calls `/api/auth/doctor/me` but backend expects `/api/doctor/auth/me`

---

### 3. Consultations Queue Endpoint Mismatch
**Frontend (DoctorDashboardPage.jsx):**
```javascript
axios.get(`${API_BASE_URL}/api/consultations/pending`, {...})
```

**Backend (ConsultationController.java):**
```java
@GetMapping("/queue")  // Under @RequestMapping("/api/consultations")
// Actual endpoint: /api/consultations/queue
```

**❌ MISMATCH:** Frontend calls `/api/consultations/pending` but backend expects `/api/consultations/queue`

---

### 4. Doctor History Endpoint Mismatch
**Frontend (ConsultationListPage.jsx):**
```javascript
axios.get(`${API_BASE_URL}/api/consultations/doctor/my-consultations`, {...})
```

**Backend (ConsultationController.java):**
```java
@GetMapping("/my-history")  // Under @RequestMapping("/api/consultations")
// Actual endpoint: /api/consultations/my-history
```

**❌ MISMATCH:** Frontend calls `/api/consultations/doctor/my-consultations` but backend expects `/api/consultations/my-history`

---

### 5. Consultation Schedule Endpoint Not Implemented
**Frontend (ConsultationDetailPage.jsx):**
```javascript
axios.put(`${API_BASE_URL}/api/consultations/${id}/schedule`, { scheduledDateTime })
```

**Backend:** ❌ NO ENDPOINT EXISTS

---

### 6. Consultation Accept Method Mismatch
**Frontend (DoctorDashboardPage.jsx & ConsultationDetailPage.jsx):**
```javascript
await axios.put(`${API_BASE_URL}/api/consultations/${consultationId}/accept`, {})
```

**Backend (ConsultationController.java):**
```java
@PostMapping("/{id}/accept")  // Uses POST, not PUT
```

**❌ MISMATCH:** Frontend uses PUT but backend expects POST

---

### 7. Consultation Complete Method Mismatch
**Frontend (ConsultationDetailPage.jsx):**
```javascript
await axios.put(`${API_BASE_URL}/api/consultations/${id}/complete`, { doctorNotes })
```

**Backend (ConsultationController.java):**
```java
@PostMapping("/{id}/complete")  // Uses POST, not PUT
```

**❌ MISMATCH:** Frontend uses PUT but backend expects POST

---

## ✅ CORRECT MAPPINGS

### Worker Authentication
| Frontend | Backend | Status |
|----------|---------|--------|
| `POST /api/auth/signup` | `POST /api/auth/signup` | ✅ |
| `POST /api/auth/login` | `POST /api/auth/login` | ✅ |
| `GET /api/auth/me` | `GET /api/auth/me` | ✅ |

### Doctor Authentication (API Service Files)
| Frontend (doctorApi.js) | Backend | Status |
|----------|---------|--------|
| `POST /api/doctor/auth/signup` | `POST /api/doctor/auth/signup` | ✅ |
| `POST /api/doctor/auth/login` | `POST /api/doctor/auth/login` | ✅ |
| `GET /api/doctor/auth/me` | `GET /api/doctor/auth/me` | ✅ |

### Patient Management
| Frontend | Backend | Status |
|----------|---------|--------|
| `POST /api/patients` | `POST /api/patients` | ✅ |
| `GET /api/patients` | `GET /api/patients` | ✅ |
| `GET /api/patients/:id` | `GET /api/patients/:id` | ✅ |

### ANC Visits
| Frontend | Backend | Status |
|----------|---------|--------|
| `POST /api/anc/register-visit` | `POST /api/anc/register-visit` | ✅ |
| `GET /api/anc/visits/:visitId` | `GET /api/anc/visits/:visitId` | ✅ |
| `GET /api/anc/patients/:patientId/visits` | `GET /api/anc/patients/:patientId/visits` | ✅ |
| `GET /api/anc/visits/high-risk` | `GET /api/anc/visits/high-risk` | ✅ |
| `GET /api/anc/visits/critical` | `GET /api/anc/visits/critical` | ✅ |

### Consultations (API Service Files)
| Frontend (consultationApi.js) | Backend | Status |
|----------|---------|--------|
| `GET /api/consultations/queue` | `GET /api/consultations/queue` | ✅ |
| `GET /api/consultations/:id` | `GET /api/consultations/:id` | ✅ |
| `POST /api/consultations/:id/accept` | `POST /api/consultations/:id/accept` | ✅ |
| `POST /api/consultations/:id/start-call` | `POST /api/consultations/:id/start-call` | ✅ |
| `POST /api/consultations/:id/complete` | `POST /api/consultations/:id/complete` | ✅ |
| `GET /api/consultations/my-history` | `GET /api/consultations/my-history` | ✅ |
| `GET /api/consultations/patient/:patientId` | `GET /api/consultations/patient/:patientId` | ✅ |

---

## 🔧 FIXES REQUIRED

### Priority 1: Fix Direct axios Calls in Pages
The following pages bypass the API service layer and have incorrect endpoints:

1. **DoctorLoginPage.jsx** - Uses wrong endpoints
2. **DoctorDashboardPage.jsx** - Uses wrong endpoints and methods
3. **ConsultationListPage.jsx** - Uses wrong endpoint
4. **ConsultationDetailPage.jsx** - Uses wrong endpoints and methods
5. **VideoConsultationPage.jsx** - Should use API service

### Priority 2: Add Missing Backend Endpoint
- Implement `PUT /api/consultations/:id/schedule` endpoint

### Priority 3: Token Storage Inconsistency
- **axiosInstance.js** looks for `anc_token`
- **Pages** use `token` directly
- Need to standardize on one key

---

## 📋 RECOMMENDED ACTIONS

1. **Update all pages to use API service files** instead of direct axios calls
2. **Fix endpoint paths** in pages that don't use API services
3. **Fix HTTP methods** (PUT → POST) for accept and complete
4. **Add schedule endpoint** to backend or remove from frontend
5. **Standardize token storage** key across all files

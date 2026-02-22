# 🌸 NeoSure - Maternal Health Frontend Specification

## 📋 Project Overview

**Project Name:** NeoSure - Antenatal Care (ANC) Management System  
**Purpose:** Web application for managing maternal health, ANC visits, AI-powered risk assessment, and doctor consultations  
**Backend:** Spring Boot REST API (Java) running on `http://localhost:8080`  
**Tech Stack:** React, Tailwind CSS, React Router, Axios  
**Authentication:** JWT Bearer tokens

---

## 🎯 Core Features

### 1. **Two User Roles**
- **ANC Workers** - Register patients, conduct ANC visits, view AI risk assessments
- **Doctors** - Review consultation queue, conduct video consultations, provide medical guidance

### 2. **Key Workflows**
- Worker signup/login → Patient management → ANC visit registration → AI risk analysis
- Doctor signup/login → Priority consultation queue → Video consultation → Complete with notes
- Real-time WebRTC video consultations with WebSocket signaling

---

## 🎨 Design System

### Color Palette (Warm Terracotta Theme)
```css
/* Primary Colors */
--primary: #C4622D;           /* Terracotta orange */
--primary-hover: #9E4A1E;     /* Darker terracotta */
--background: #F5EBE0;         /* Warm beige */

/* Text Colors */
--text-dark: #2C1A0E;         /* Dark brown */
--text-medium: #5C4A42;       /* Medium brown */
--text-light: #8B7355;        /* Light brown */

/* Neutral Colors */
--white: #FFFFFF;
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;

/* Status Colors */
--success: #10B981;           /* Green */
--warning: #F59E0B;           /* Amber */
--error: #EF4444;             /* Red */
--info: #3B82F6;              /* Blue */

/* Risk Level Colors */
--risk-low: #10B981;          /* Green */
--risk-medium: #F59E0B;       /* Amber */
--risk-high: #F97316;         /* Orange */
--risk-critical: #DC2626;     /* Red */
```

### Typography
- **Font Family:** -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
- **Headings:** Font weight 600-700
- **Body:** Font weight 400
- **Small text:** 12-14px
- **Regular text:** 14-16px
- **Headings:** 18-28px

### Component Style Guidelines
- **Border Radius:** 8px for cards, 4px for buttons/inputs
- **Shadows:** `0 2px 4px rgba(0,0,0,0.1)` for cards
- **Spacing:** Use 4px increments (8px, 12px, 16px, 20px, 24px)
- **Buttons:** Solid primary color, white text, hover state darker
- **Forms:** White background, border on inputs, clear labels

---

## 🔐 Authentication & Authorization

### JWT Token Management

**Storage Keys (localStorage):**
- `anc_token` - JWT token string
- `anc_role` - User role: "WORKER" or "DOCTOR"
- `anc_user` - User profile object (JSON stringified)

**HTTP Headers:**
```javascript
Authorization: Bearer <token>
Content-Type: application/json
```

**Token Flow:**
1. User logs in → Backend returns `{ token, role, ...userInfo }`
2. Store token, role, and user info in localStorage
3. Add `Authorization: Bearer <token>` header to all authenticated requests
4. On 401 response → Clear localStorage and redirect to login

---

## 📡 API Endpoints Reference

### Base URL
```
http://localhost:8080
```

### 1. Worker Authentication

#### POST `/api/auth/signup`
**Description:** Register new ANC worker  
**Auth Required:** No

**Request Body:**
```json
{
  "fullName": "Priya Sharma",
  "phone": "9876543210",
  "email": "priya@health.gov.in",
  "password": "SecurePass123",
  "healthCenter": "Primary Health Center Bangalore",
  "district": "Bangalore Urban"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "workerId": "550e8400-e29b-41d4-a716-446655440000",
  "fullName": "Priya Sharma",
  "phone": "9876543210",
  "email": "priya@health.gov.in",
  "healthCenter": "Primary Health Center Bangalore",
  "district": "Bangalore Urban",
  "message": "Signup successful"
}
```

**Validation Rules:**
- Phone: 10 digits, starts with 6-9
- Password: Minimum 8 characters
- All fields required

---

#### POST `/api/auth/login`
**Description:** Worker login  
**Auth Required:** No

**Request Body:**
```json
{
  "phone": "9876543210",
  "password": "SecurePass123"
}
```

**Response (200):** Same as signup response

**Error (401):**
```json
{
  "message": "Invalid credentials"
}
```

---

#### GET `/api/auth/me`
**Description:** Get worker profile  
**Auth Required:** Yes (Worker token)

**Response (200):**
```json
{
  "workerId": "550e8400-e29b-41d4-a716-446655440000",
  "fullName": "Priya Sharma",
  "phone": "9876543210",
  "email": "priya@health.gov.in",
  "healthCenter": "Primary Health Center Bangalore",
  "district": "Bangalore Urban"
}
```

---

### 2. Doctor Authentication

#### POST `/api/doctor/auth/signup`
**Description:** Register new doctor  
**Auth Required:** No

**Request Body:**
```json
{
  "fullName": "Dr. Rajesh Kumar",
  "phone": "9988776655",
  "email": "rajesh@hospital.in",
  "password": "DoctorPass123",
  "specialization": "Obstetrics & Gynaecology",
  "hospital": "District Hospital",
  "district": "Bangalore Urban",
  "registrationNo": "KA-12345"
}
```

**Response (201):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "DOCTOR",
  "doctorId": "d50e8400-e29b-41d4-a716-446655440001",
  "fullName": "Dr. Rajesh Kumar",
  "phone": "9988776655",
  "email": "rajesh@hospital.in",
  "specialization": "Obstetrics & Gynaecology",
  "hospital": "District Hospital",
  "district": "Bangalore Urban",
  "registrationNo": "KA-12345",
  "isAvailable": true,
  "message": "Doctor registered successfully"
}
```

---

#### POST `/api/doctor/auth/login`
**Description:** Doctor login  
**Auth Required:** No

**Request Body:**
```json
{
  "phone": "9988776655",
  "password": "DoctorPass123"
}
```

**Response (200):** Same as doctor signup response

---

#### GET `/api/doctor/auth/me`
**Description:** Get doctor profile  
**Auth Required:** Yes (Doctor token)

**Response (200):** Same structure as doctor signup response (without token)

---

### 3. Patient Management

#### POST `/api/patients`
**Description:** Create new patient  
**Auth Required:** Yes (Worker token)

**Request Body:**
```json
{
  "fullName": "Lakshmi Devi",
  "phone": "9123456789",
  "age": 26,
  "address": "123 Main Street",
  "village": "Koramangala",
  "district": "Bangalore Urban",
  "lmpDate": "2024-01-15",
  "eddDate": "2024-10-22",
  "bloodGroup": "O+"
}
```

**Response (200):**
```json
{
  "patientId": "p50e8400-e29b-41d4-a716-446655440002",
  "workerId": "550e8400-e29b-41d4-a716-446655440000",
  "fullName": "Lakshmi Devi",
  "phone": "9123456789",
  "age": 26,
  "address": "123 Main Street",
  "village": "Koramangala",
  "district": "Bangalore Urban",
  "lmpDate": "2024-01-15",
  "eddDate": "2024-10-22",
  "bloodGroup": "O+",
  "createdAt": "2024-02-22T10:30:00"
}
```

---

#### GET `/api/patients`
**Description:** Get all patients for logged-in worker  
**Auth Required:** Yes (Worker token)

**Response (200):**
```json
[
  {
    "patientId": "p50e8400-e29b-41d4-a716-446655440002",
    "fullName": "Lakshmi Devi",
    "phone": "9123456789",
    "age": 26,
    "village": "Koramangala",
    "district": "Bangalore Urban",
    "lmpDate": "2024-01-15",
    "eddDate": "2024-10-22",
    "bloodGroup": "O+",
    "createdAt": "2024-02-22T10:30:00"
  }
]
```

---

#### GET `/api/patients/{id}`
**Description:** Get patient by ID  
**Auth Required:** Yes (Worker token)

**Response (200):** Same structure as single patient object above

---

### 4. ANC Visit Registration

#### POST `/api/anc/register-visit`
**Description:** Register ANC visit with AI risk assessment  
**Auth Required:** Yes (Worker token)

**Request Body (Complex - Nested Structure):**
```json
{
  "patientId": "p50e8400-e29b-41d4-a716-446655440002",
  "patientName": "Lakshmi Devi",
  "workerId": "550e8400-e29b-41d4-a716-446655440000",
  "phcId": "PHC-BLR-001",
  "structured_data": {
    "patient_info": {
      "name": "Lakshmi Devi",
      "age": 26,
      "gestational_age_weeks": 24,
      "gravida": 2,
      "para": 1,
      "abortions": 0,
      "living_children": 1
    },
    "vitals": {
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 80,
      "pulse_rate": 78,
      "temperature": 98.6,
      "weight_kg": 65,
      "height_cm": 160,
      "bmi": 25.4,
      "respiratory_rate": 18
    },
    "current_symptoms": {
      "complaints": ["Mild headache", "Fatigue"],
      "severity": "mild",
      "duration_days": 2
    },
    "obstetric_history": {
      "previous_pregnancies": 1,
      "previous_deliveries": 1,
      "previous_complications": "None",
      "delivery_mode_last": "Normal vaginal delivery"
    },
    "medical_history": {
      "chronic_conditions": [],
      "allergies": [],
      "current_medications": ["Folic acid", "Iron supplements"],
      "past_surgeries": []
    },
    "pregnancy_details": {
      "lmp_date": "2024-01-15",
      "edd_date": "2024-10-22",
      "current_gestational_age": "24 weeks",
      "pregnancy_complications": []
    },
    "lab_reports": {
      "hemoglobin": 11.5,
      "blood_group": "O+",
      "blood_sugar_fasting": 90,
      "urine_protein": "Negative",
      "hiv_status": "Negative",
      "hbsag_status": "Negative"
    }
  }
}
```

**Response (201):**
```json
{
  "visitId": "v50e8400-e29b-41d4-a716-446655440003",
  "patientId": "p50e8400-e29b-41d4-a716-446655440002",
  "patientName": "Lakshmi Devi",
  "status": "AI_ANALYZED",
  "riskAssessment": {
    "risk_level": "MEDIUM",
    "risk_score": 45,
    "risk_factors": [
      "Low hemoglobin (11.5 g/dL)",
      "BMI slightly elevated (25.4)"
    ],
    "recommendations": [
      "Continue iron supplementation",
      "Monitor blood pressure regularly",
      "Schedule follow-up in 2 weeks"
    ],
    "requires_doctor_consultation": true,
    "urgency": "routine",
    "summary": "Patient shows moderate risk factors requiring routine monitoring."
  },
  "savedAt": "2024-02-22T11:00:00",
  "message": "Visit registered and AI analysis completed successfully"
}
```

**Risk Levels:**
- `LOW` - Green badge, routine care
- `MEDIUM` - Amber badge, increased monitoring
- `HIGH` - Orange badge, doctor consultation recommended
- `CRITICAL` - Red badge, immediate doctor consultation required

---

#### GET `/api/anc/visits/{visitId}`
**Description:** Get visit by ID  
**Auth Required:** Yes

**Response (200):** Full visit entity with all structured data

---

#### GET `/api/anc/patients/{patientId}/visits`
**Description:** Get all visits for a patient  
**Auth Required:** Yes

**Response (200):** Array of visit entities

---

#### GET `/api/anc/visits/high-risk`
**Description:** Get all high-risk visits  
**Auth Required:** Yes

**Response (200):** Array of high-risk visit entities

---

#### GET `/api/anc/visits/critical`
**Description:** Get all critical visits  
**Auth Required:** Yes

**Response (200):** Array of critical visit entities

---

### 5. Doctor Consultations

#### GET `/api/consultations/queue`
**Description:** Get doctor's priority consultation queue  
**Auth Required:** Yes (Doctor token)

**Response (200):**
```json
[
  {
    "consultationId": "c50e8400-e29b-41d4-a716-446655440004",
    "visitId": "v50e8400-e29b-41d4-a716-446655440003",
    "patientId": "p50e8400-e29b-41d4-a716-446655440002",
    "patientName": "Lakshmi Devi",
    "patientAge": 26,
    "gestationalAge": "24 weeks",
    "riskLevel": "HIGH",
    "riskScore": 75,
    "status": "PENDING",
    "createdAt": "2024-02-22T11:00:00",
    "district": "Bangalore Urban",
    "urgency": "urgent"
  }
]
```

**Consultation Statuses:**
- `PENDING` - Waiting for doctor to accept
- `ACCEPTED` - Doctor accepted, not started
- `IN_PROGRESS` - Video call in progress
- `COMPLETED` - Consultation finished with notes

---

#### GET `/api/consultations/{id}`
**Description:** Get full consultation details  
**Auth Required:** Yes (Doctor token)

**Response (200):**
```json
{
  "consultationId": "c50e8400-e29b-41d4-a716-446655440004",
  "visitId": "v50e8400-e29b-41d4-a716-446655440003",
  "patientId": "p50e8400-e29b-41d4-a716-446655440002",
  "patientName": "Lakshmi Devi",
  "patientAge": 26,
  "patientPhone": "9123456789",
  "gestationalAge": "24 weeks",
  "riskLevel": "HIGH",
  "riskScore": 75,
  "riskFactors": [
    "Low hemoglobin (11.5 g/dL)",
    "Previous pregnancy complications"
  ],
  "aiRecommendations": [
    "Immediate doctor consultation",
    "Monitor blood pressure closely"
  ],
  "clinicalSummary": "26-year-old G2P1 at 24 weeks gestation...",
  "status": "PENDING",
  "createdAt": "2024-02-22T11:00:00",
  "district": "Bangalore Urban"
}
```

---

#### POST `/api/consultations/{id}/accept`
**Description:** Doctor accepts consultation  
**Auth Required:** Yes (Doctor token)

**Response (200):**
```json
{
  "consultationId": "c50e8400-e29b-41d4-a716-446655440004",
  "status": "ACCEPTED",
  "doctorId": "d50e8400-e29b-41d4-a716-446655440001",
  "doctorName": "Dr. Rajesh Kumar",
  "acceptedAt": "2024-02-22T11:05:00",
  "message": "Consultation accepted successfully"
}
```

---

#### POST `/api/consultations/{id}/start-call`
**Description:** Start video consultation (generates WebRTC room)  
**Auth Required:** Yes (Doctor token)

**Response (200):**
```json
{
  "consultationId": "c50e8400-e29b-41d4-a716-446655440004",
  "status": "IN_PROGRESS",
  "videoRoomUrl": "https://neosure.daily.co/consultation-c50e8400",
  "doctorToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "workerToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "startedAt": "2024-02-22T11:10:00",
  "message": "Video call started"
}
```

---

#### POST `/api/consultations/{id}/complete`
**Description:** Complete consultation with doctor notes  
**Auth Required:** Yes (Doctor token)

**Request Body:**
```json
{
  "doctorNotes": "Patient shows signs of mild anemia. Advised increased iron intake.",
  "diagnosis": "Mild anemia in pregnancy",
  "actionPlan": "Continue iron supplements, follow-up in 2 weeks, monitor hemoglobin levels"
}
```

**Response (200):**
```json
{
  "consultationId": "c50e8400-e29b-41d4-a716-446655440004",
  "status": "COMPLETED",
  "doctorNotes": "Patient shows signs of mild anemia...",
  "diagnosis": "Mild anemia in pregnancy",
  "actionPlan": "Continue iron supplements...",
  "completedAt": "2024-02-22T11:30:00",
  "message": "Consultation completed successfully"
}
```

---

#### GET `/api/consultations/my-history`
**Description:** Get doctor's consultation history  
**Auth Required:** Yes (Doctor token)

**Response (200):** Array of consultation objects (all statuses)

---

#### GET `/api/consultations/patient/{patientId}`
**Description:** Get all consultations for a patient  
**Auth Required:** Yes (Worker or Doctor token)

**Response (200):** Array of consultation objects for the patient

---

## 🖥️ Page Structure & Routes

### Public Routes (No Auth Required)

#### 1. Landing Page `/`
**Purpose:** Marketing page with app overview  
**Components:**
- Hero section with app description
- Features showcase (3-4 key features)
- Call-to-action buttons: "Worker Login" and "Doctor Login"
- Professional warm terracotta theme

**Design:**
- Background: Warm beige (#F5EBE0)
- Primary buttons: Terracotta (#C4622D)
- Clean, minimal layout
- Responsive design

---

#### 2. Worker Login `/worker/login`
**Purpose:** Worker authentication  
**Form Fields:**
- Phone number (10 digits, starts with 6-9)
- Password (minimum 8 characters)
- "Sign In" button
- Link to signup page

**Behavior:**
- POST to `/api/auth/login`
- On success: Store token, role="WORKER", user info → Redirect to `/worker/dashboard`
- On error: Show error message

---

#### 3. Worker Signup `/worker/signup`
**Purpose:** Worker registration  
**Form Fields:**
- Full Name
- Phone Number
- Email
- Password
- Health Center
- District
- "Sign Up" button
- Link to login page

**Behavior:**
- POST to `/api/auth/signup`
- On success: Store token, role="WORKER", user info → Redirect to `/worker/dashboard`
- On error: Show validation errors

---

#### 4. Doctor Login `/doctor/login`
**Purpose:** Doctor authentication  
**Form Fields:**
- Phone number (10 digits)
- Password
- "Sign In" button
- Link to signup page

**Behavior:**
- POST to `/api/doctor/auth/login`
- On success: Store token, role="DOCTOR", user info → Redirect to `/doctor/dashboard`
- On error: Show error message

---

#### 5. Doctor Signup `/doctor/signup`
**Purpose:** Doctor registration  
**Form Fields:**
- Full Name
- Phone Number
- Email
- Password
- Specialization
- Hospital
- District
- Registration Number
- "Sign Up" button
- Link to login page

**Behavior:**
- POST to `/api/doctor/auth/signup`
- On success: Store token, role="DOCTOR", user info → Redirect to `/doctor/dashboard`
- On error: Show validation errors

---

### Worker Protected Routes (Requires Worker Token)

#### 6. Worker Dashboard `/worker/dashboard`
**Purpose:** Overview of worker's patients and recent activities  
**Components:**
- Welcome message with worker name
- Statistics cards:
  - Total patients registered
  - Recent visits count
  - High-risk patients count
- Quick action buttons:
  - "Register New Patient"
  - "View All Patients"
- Recent patients list (last 5)

**API Calls:**
- GET `/api/patients` - Fetch all patients
- GET `/api/auth/me` - Fetch worker profile

---

#### 7. Patient List `/worker/patients`
**Purpose:** View all patients registered by worker  
**Components:**
- Search bar (filter by name/phone)
- Patient cards/table with:
  - Patient name
  - Age
  - Phone number
  - Village
  - EDD date
  - Blood group
  - "View Details" button
- "Add New Patient" button

**API Calls:**
- GET `/api/patients`

---

#### 8. Patient Create `/worker/patients/new`
**Purpose:** Register new patient  
**Form Fields:**
- Full Name
- Phone Number
- Age
- Address
- Village
- District
- LMP Date (date picker)
- EDD Date (date picker)
- Blood Group (dropdown: A+, A-, B+, B-, O+, O-, AB+, AB-)
- "Register Patient" button

**Behavior:**
- POST to `/api/patients`
- On success: Redirect to `/worker/patients/{patientId}`
- On error: Show validation errors

---

#### 9. Patient Detail `/worker/patients/:id`
**Purpose:** View patient details and visit history  
**Components:**
- Patient information card:
  - Name, age, phone
  - Address, village, district
  - LMP, EDD, blood group
  - Registration date
- Visit history section:
  - List of all ANC visits
  - Each visit shows: Date, risk level, status
  - Click to view visit details
- Action buttons:
  - "Register New Visit" → Navigate to visit form

**API Calls:**
- GET `/api/patients/{id}`
- GET `/api/anc/patients/{patientId}/visits`

---

#### 10. ANC Visit Form `/worker/visits/new?patientId={id}`
**Purpose:** Register new ANC visit with comprehensive data collection  
**Form Structure (Multi-step or Single Page):**

**Step 1: Patient Info (Pre-filled from patient record)**
- Name, Age, Gestational Age
- Gravida, Para, Abortions, Living Children

**Step 2: Vitals**
- Blood Pressure (Systolic/Diastolic)
- Pulse Rate
- Temperature
- Weight (kg)
- Height (cm)
- BMI (auto-calculated)
- Respiratory Rate

**Step 3: Current Symptoms**
- Complaints (text area or checkboxes)
- Severity (dropdown: mild, moderate, severe)
- Duration (days)

**Step 4: Obstetric History**
- Previous Pregnancies
- Previous Deliveries
- Previous Complications
- Last Delivery Mode

**Step 5: Medical History**
- Chronic Conditions (multi-select)
- Allergies (text input)
- Current Medications (text area)
- Past Surgeries (text area)

**Step 6: Pregnancy Details**
- LMP Date
- EDD Date
- Current Gestational Age
- Pregnancy Complications (text area)

**Step 7: Lab Reports**
- Hemoglobin
- Blood Group
- Blood Sugar (Fasting)
- Urine Protein
- HIV Status
- HBsAg Status

**Submit Button:** "Register Visit & Get AI Analysis"

**Behavior:**
- POST to `/api/anc/register-visit`
- Show loading spinner during AI analysis
- On success: Redirect to `/worker/visits/{visitId}/result`
- On error: Show error message

---

#### 11. Visit Result `/worker/visits/:visitId/result`
**Purpose:** Display AI risk assessment results  
**Components:**
- Patient information summary
- Risk level badge (color-coded):
  - LOW: Green
  - MEDIUM: Amber
  - HIGH: Orange
  - CRITICAL: Red
- Risk score (0-100)
- Risk factors list (bullet points)
- AI recommendations list
- Doctor consultation status:
  - If required: "Doctor consultation recommended" badge
  - Urgency level: routine/urgent/immediate
- Action buttons:
  - "View Full Visit Details"
  - "Back to Patient Profile"
  - "Register Another Visit"

**API Calls:**
- GET `/api/anc/visits/{visitId}`

---

### Doctor Protected Routes (Requires Doctor Token)

#### 12. Doctor Dashboard `/doctor/dashboard`
**Purpose:** Overview of consultation queue and statistics  
**Components:**
- Welcome message with doctor name
- Statistics cards:
  - Pending consultations count
  - Today's consultations count
  - Total consultations completed
- Priority consultation queue (top 5):
  - Patient name, age
  - Risk level badge
  - Gestational age
  - Time waiting
  - "View Details" button
- Quick action button: "View Full Queue"

**API Calls:**
- GET `/api/consultations/queue`
- GET `/api/doctor/auth/me`

---

#### 13. Consultation Queue `/doctor/consultations`
**Purpose:** Full priority consultation queue  
**Components:**
- Filter tabs:
  - All
  - Pending
  - Accepted
  - In Progress
  - Completed
- Sort options:
  - By risk level (Critical → Low)
  - By time (Oldest first)
- Consultation cards showing:
  - Patient name, age
  - Risk level badge (color-coded)
  - Risk score
  - Gestational age
  - District
  - Time created
  - Status badge
  - "View Details" button

**API Calls:**
- GET `/api/consultations/queue`

---

#### 14. Consultation Detail `/doctor/consultations/:id`
**Purpose:** Full consultation details with patient history  
**Components:**
- Patient information section:
  - Name, age, phone
  - Gestational age
  - District
- Risk assessment section:
  - Risk level badge
  - Risk score
  - Risk factors list
  - AI recommendations
- Clinical summary (generated by AI)
- Visit details (vitals, symptoms, history)
- Action buttons (based on status):
  - PENDING: "Accept Consultation" button
  - ACCEPTED: "Start Video Call" button
  - IN_PROGRESS: "Join Video Call" button
  - COMPLETED: Show doctor notes, diagnosis, action plan

**API Calls:**
- GET `/api/consultations/{id}`
- POST `/api/consultations/{id}/accept` (on accept)
- POST `/api/consultations/{id}/start-call` (on start call)

---

#### 15. Video Consultation `/doctor/consultations/:id/video`
**Purpose:** WebRTC video consultation interface  
**Components:**
- Video grid:
  - Doctor video (large)
  - Worker/Patient video (smaller)
- Control buttons:
  - Mute/Unmute microphone
  - Enable/Disable camera
  - End call
- Patient information sidebar:
  - Name, age, gestational age
  - Risk level
  - Key risk factors
  - Clinical summary
- Notes section (collapsible):
  - Text area for doctor notes during call
  - Auto-save functionality

**WebRTC Implementation:**
- Use WebSocket connection to `/ws/signaling`
- Exchange ICE candidates and SDP offers/answers
- Use Simple-Peer or native WebRTC APIs
- Handle connection states (connecting, connected, disconnected)

**Behavior:**
- On "End Call": Show completion form modal
- Completion form fields:
  - Doctor Notes (required)
  - Diagnosis (required)
  - Action Plan (required)
  - "Complete Consultation" button
- POST to `/api/consultations/{id}/complete`
- On success: Redirect to `/doctor/consultations/{id}` (now showing completed status)

---

#### 16. Consultation History `/doctor/history`
**Purpose:** Doctor's past consultations  
**Components:**
- Date range filter
- Status filter (All, Completed, Cancelled)
- Consultation cards showing:
  - Patient name
  - Date completed
  - Risk level
  - Diagnosis
  - "View Details" button

**API Calls:**
- GET `/api/consultations/my-history`

---

## 🔧 Technical Implementation Details

### State Management
**Recommended:** React Context API or Zustand

**Global State:**
- `authState`: { token, role, user, isAuthenticated }
- `patientState`: { patients, selectedPatient }
- `consultationState`: { queue, selectedConsultation }

### API Service Layer
Create `src/services/api.js`:

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:8080';

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('anc_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### API Service Functions

```javascript
// Worker Auth
export const workerSignup = (data) => api.post('/api/auth/signup', data);
export const workerLogin = (data) => api.post('/api/auth/login', data);
export const getWorkerProfile = () => api.get('/api/auth/me');

// Doctor Auth
export const doctorSignup = (data) => api.post('/api/doctor/auth/signup', data);
export const doctorLogin = (data) => api.post('/api/doctor/auth/login', data);
export const getDoctorProfile = () => api.get('/api/doctor/auth/me');

// Patients
export const createPatient = (data) => api.post('/api/patients', data);
export const getPatients = () => api.get('/api/patients');
export const getPatient = (id) => api.get(`/api/patients/${id}`);

// ANC Visits
export const registerVisit = (data) => api.post('/api/anc/register-visit', data);
export const getVisit = (id) => api.get(`/api/anc/visits/${id}`);
export const getPatientVisits = (patientId) => api.get(`/api/anc/patients/${patientId}/visits`);
export const getHighRiskVisits = () => api.get('/api/anc/visits/high-risk');
export const getCriticalVisits = () => api.get('/api/anc/visits/critical');

// Consultations
export const getConsultationQueue = () => api.get('/api/consultations/queue');
export const getConsultation = (id) => api.get(`/api/consultations/${id}`);
export const acceptConsultation = (id) => api.post(`/api/consultations/${id}/accept`);
export const startCall = (id) => api.post(`/api/consultations/${id}/start-call`);
export const completeConsultation = (id, notes) => api.post(`/api/consultations/${id}/complete`, notes);
export const getDoctorHistory = () => api.get('/api/consultations/my-history');
export const getPatientConsultations = (patientId) => api.get(`/api/consultations/patient/${patientId}`);
```

---

### Protected Route Component

```javascript
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requiredRole }) => {
  const token = localStorage.getItem('anc_token');
  const role = localStorage.getItem('anc_role');

  if (!token) {
    return <Navigate to="/" replace />;
  }

  if (requiredRole && role !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

---

### WebSocket Connection (for Video Signaling)

```javascript
import SockJS from 'sockjs-client';
import { Stomp } from '@stomp/stompjs';

let stompClient = null;

export const connectWebSocket = (consultationId, onMessage) => {
  const socket = new SockJS('http://localhost:8080/ws');
  stompClient = Stomp.over(socket);

  stompClient.connect({}, () => {
    // Subscribe to consultation-specific channel
    stompClient.subscribe(`/topic/consultation/${consultationId}`, (message) => {
      onMessage(JSON.parse(message.body));
    });
  });
};

export const sendSignal = (consultationId, signal) => {
  if (stompClient && stompClient.connected) {
    stompClient.send(
      `/app/signal/${consultationId}`,
      {},
      JSON.stringify(signal)
    );
  }
};

export const disconnectWebSocket = () => {
  if (stompClient) {
    stompClient.disconnect();
  }
};
```

---

## 🎨 UI Component Library Recommendations

### Suggested Libraries
- **Tailwind CSS** - Utility-first CSS framework
- **Headless UI** - Unstyled accessible components
- **React Hook Form** - Form validation
- **React Router v6** - Routing
- **Axios** - HTTP client
- **date-fns** - Date formatting
- **SockJS + STOMP** - WebSocket for video signaling
- **Simple-Peer** - WebRTC wrapper

---

## 📱 Responsive Design Requirements

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Mobile Considerations
- Stack cards vertically
- Hamburger menu for navigation
- Touch-friendly button sizes (min 44px)
- Simplified tables (convert to cards on mobile)
- Bottom navigation for main actions

---

## 🔔 User Feedback & Notifications

### Toast Notifications
Show toast messages for:
- Successful actions (green)
- Errors (red)
- Warnings (amber)
- Info messages (blue)

**Examples:**
- "Patient registered successfully"
- "Visit registered and AI analysis completed"
- "Consultation accepted"
- "Video call started"
- "Consultation completed"

### Loading States
- Show spinners during API calls
- Skeleton loaders for lists
- "Analyzing..." message during AI risk assessment
- "Connecting..." during video call setup

### Error Handling
- Display user-friendly error messages
- Validation errors inline on forms
- Network error fallback UI
- 404 page for invalid routes

---

## 🧪 Testing Checklist

### Authentication Flow
- [ ] Worker signup with validation
- [ ] Worker login with correct credentials
- [ ] Worker login with incorrect credentials
- [ ] Doctor signup with validation
- [ ] Doctor login with correct credentials
- [ ] Token storage in localStorage
- [ ] Auto-redirect on 401 errors
- [ ] Logout functionality

### Worker Flow
- [ ] View dashboard with statistics
- [ ] View patient list
- [ ] Create new patient
- [ ] View patient details
- [ ] Register ANC visit with all fields
- [ ] View AI risk assessment results
- [ ] View visit history for patient

### Doctor Flow
- [ ] View dashboard with queue preview
- [ ] View full consultation queue
- [ ] Filter consultations by status
- [ ] View consultation details
- [ ] Accept consultation
- [ ] Start video call
- [ ] Complete consultation with notes
- [ ] View consultation history

### Video Consultation
- [ ] WebSocket connection established
- [ ] Video streams displayed
- [ ] Audio/video controls work
- [ ] End call and show completion form
- [ ] Submit completion form

---

## 📊 Data Validation Rules

### Phone Number
- Pattern: `^[6-9]\d{9}$`
- Must be 10 digits
- Must start with 6, 7, 8, or 9

### Password
- Minimum 8 characters
- Required for signup/login

### Email
- Valid email format
- Required for signup

### Dates
- LMP Date: Must be in the past
- EDD Date: Must be in the future
- Format: YYYY-MM-DD

### Vitals
- Blood Pressure: Systolic 70-200, Diastolic 40-130
- Pulse Rate: 40-200 bpm
- Temperature: 95-105°F
- Weight: 30-200 kg
- Height: 100-220 cm
- BMI: Auto-calculated (weight / (height/100)²)

### Lab Reports
- Hemoglobin: 5-20 g/dL
- Blood Sugar: 50-400 mg/dL
- Blood Group: A+, A-, B+, B-, O+, O-, AB+, AB-

---

## 🚀 Deployment Considerations

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_WS_URL=http://localhost:8080/ws
```

### Build Command
```bash
npm run build
```

### Production Checklist
- [ ] Update API base URL to production backend
- [ ] Enable HTTPS for WebSocket connections
- [ ] Add error tracking (Sentry)
- [ ] Add analytics (Google Analytics)
- [ ] Optimize images and assets
- [ ] Enable service worker for PWA
- [ ] Test on multiple browsers
- [ ] Test on mobile devices

---

## 📝 Sample User Flows

### Flow 1: Worker Registers Patient and Conducts Visit

1. Worker logs in at `/worker/login`
2. Redirected to `/worker/dashboard`
3. Clicks "Register New Patient"
4. Fills patient form at `/worker/patients/new`
5. Submits → Patient created
6. Redirected to `/worker/patients/{id}`
7. Clicks "Register New Visit"
8. Fills comprehensive visit form at `/worker/visits/new?patientId={id}`
9. Submits → Shows loading "Analyzing with AI..."
10. Redirected to `/worker/visits/{visitId}/result`
11. Views risk assessment: HIGH risk, doctor consultation required
12. System automatically creates consultation for doctor

### Flow 2: Doctor Reviews and Completes Consultation

1. Doctor logs in at `/doctor/login`
2. Redirected to `/doctor/dashboard`
3. Sees pending consultation in queue (HIGH risk patient)
4. Clicks "View Details"
5. Reviews patient history, vitals, AI recommendations at `/doctor/consultations/{id}`
6. Clicks "Accept Consultation"
7. Status changes to ACCEPTED
8. Clicks "Start Video Call"
9. Redirected to `/doctor/consultations/{id}/video`
10. Video call connects via WebRTC
11. Doctor discusses with worker/patient
12. Takes notes during call
13. Clicks "End Call"
14. Completion form appears
15. Fills: Doctor Notes, Diagnosis, Action Plan
16. Submits → Consultation marked COMPLETED
17. Redirected to consultation detail page showing completed status

---

## 🎯 Priority Features for MVP

### Must Have (P0)
- ✅ Worker authentication (signup/login)
- ✅ Doctor authentication (signup/login)
- ✅ Patient registration
- ✅ ANC visit registration with AI analysis
- ✅ Risk assessment display
- ✅ Doctor consultation queue
- ✅ Accept consultation
- ✅ Complete consultation with notes

### Should Have (P1)
- ✅ Video consultation (WebRTC)
- ✅ Patient list and search
- ✅ Visit history per patient
- ✅ Doctor consultation history
- ✅ Dashboard statistics

### Nice to Have (P2)
- 📊 Advanced analytics dashboard
- 📧 Email notifications
- 📱 Push notifications
- 🔔 Real-time updates for queue changes
- 📄 PDF report generation
- 🌐 Multi-language support
- 🔍 Advanced search and filters

---

## 🐛 Known Backend Behaviors

### Important Notes
1. **Phone Number Validation:** Backend strictly validates Indian phone numbers (10 digits, starts with 6-9)
2. **Date Format:** Backend expects dates in `YYYY-MM-DD` format
3. **UUID vs String:** Some IDs are UUIDs, some are Strings - check API responses
4. **Token Expiry:** JWT tokens expire after 24 hours - handle 401 responses
5. **CORS:** Backend allows all origins (`*`) - no CORS issues expected
6. **AI Analysis:** Visit registration may take 3-5 seconds for AI analysis
7. **WebSocket:** Use SockJS for WebSocket connection (not native WebSocket)
8. **Video Tokens:** Video room tokens are generated by backend, not frontend

---

## 📞 Support & Documentation

### Backend API Documentation
- **Swagger UI:** http://localhost:8080/swagger-ui/index.html
- **API Tester:** http://localhost:8080/api-tester.html
- **OpenAPI JSON:** http://localhost:8080/v3/api-docs

### Backend Repository Structure
```
Backend/
├── src/main/java/com/anc/
│   ├── controller/     # REST endpoints
│   ├── service/        # Business logic
│   ├── repository/     # Database access
│   ├── entity/         # Database models
│   ├── dto/            # Request/Response objects
│   ├── security/       # JWT & auth config
│   └── config/         # App configuration
└── src/main/resources/
    ├── application.yml # App settings
    └── static/         # Static files
```

---

## ✅ Final Checklist for Lovable

### Before Starting Development
- [ ] Read this entire specification
- [ ] Review API endpoints in Swagger UI
- [ ] Test API endpoints using API Tester
- [ ] Understand authentication flow
- [ ] Understand data structures (DTOs)
- [ ] Review color palette and design system

### During Development
- [ ] Use exact API endpoint paths
- [ ] Use exact request/response field names (camelCase)
- [ ] Store tokens with correct localStorage keys
- [ ] Add Authorization header to authenticated requests
- [ ] Handle 401 errors with logout
- [ ] Show loading states during API calls
- [ ] Display user-friendly error messages
- [ ] Validate forms before submission
- [ ] Use warm terracotta color theme
- [ ] Make responsive for mobile/tablet/desktop

### After Development
- [ ] Test all user flows end-to-end
- [ ] Test on different screen sizes
- [ ] Test error scenarios
- [ ] Test with real backend (not mocked)
- [ ] Verify token storage and retrieval
- [ ] Verify logout clears all data
- [ ] Check console for errors
- [ ] Optimize performance

---

## 🎉 Summary

This specification provides everything needed to build the NeoSure frontend:

1. **Complete API documentation** with request/response examples
2. **16 pages** with detailed component requirements
3. **Design system** with exact colors and styles
4. **Authentication flow** with token management
5. **Data validation rules** for all forms
6. **WebRTC video consultation** implementation guide
7. **Sample user flows** for testing
8. **Technical implementation** details with code examples

**Backend is ready and running on port 8080. Start building! 🚀**

---

**Questions or Issues?**
- Check Swagger UI for live API documentation
- Use API Tester to test endpoints manually
- Review existing frontend code in `Frontend/anc-frontend/src/` for reference
- Backend logs show detailed error messages

**Good luck building NeoSure! 💪**

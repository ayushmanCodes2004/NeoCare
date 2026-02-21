# NeoSure Doctor Dashboard & Video Consultation - Complete Specification

## Overview
Professional dashboard for doctors to receive consultation requests from ANC workers for high-risk pregnancy cases and conduct video consultations.

---

## System Architecture

### User Roles
1. **ANC Worker** - Registers patients, conducts visits, requests doctor consultations
2. **Doctor** - Reviews high-risk cases, conducts video consultations, provides medical advice

### Workflow
```
ANC Worker → Registers Visit → AI Analysis → High/Critical Risk Detected
    ↓
Request Doctor Consultation
    ↓
Doctor Receives Request → Reviews Case → Schedules/Starts Video Call
    ↓
Video Consultation (WebRTC)
    ↓
Doctor Provides Notes, Prescription, Recommendations
    ↓
ANC Worker Receives Consultation Report
```

---

## Backend API Endpoints

### Doctor Authentication (`/api/auth/doctor`)
- `POST /api/auth/doctor/signup` - Doctor registration
- `POST /api/auth/doctor/login` - Doctor login
- `GET /api/auth/doctor/me` - Get doctor profile
- `PUT /api/auth/doctor/availability` - Update availability status

### Consultation APIs (`/api/consultations`)
- `POST /api/consultations/request` - ANC worker requests consultation
- `GET /api/consultations/pending` - Get pending consultation requests
- `GET /api/consultations/my-consultations` - Get doctor's consultations
- `GET /api/consultations/{id}` - Get consultation details
- `PUT /api/consultations/{id}/accept` - Doctor accepts consultation
- `PUT /api/consultations/{id}/start` - Start video consultation
- `PUT /api/consultations/{id}/complete` - Complete consultation with notes
- `PUT /api/consultations/{id}/cancel` - Cancel consultation

### Video Call APIs (`/api/video`)
- `POST /api/video/create-room` - Create video call room
- `GET /api/video/room/{roomId}` - Get room details
- `POST /api/video/join/{roomId}` - Join video call
- `DELETE /api/video/room/{roomId}` - End video call

### Doctor Dashboard APIs (`/api/doctor`)
- `GET /api/doctor/stats` - Get dashboard statistics
- `GET /api/doctor/high-risk-cases` - Get all high-risk cases
- `GET /api/doctor/critical-cases` - Get critical cases
- `GET /api/doctor/recent-consultations` - Get recent consultations

---

## Database Schema

### doctors Table
```sql
CREATE TABLE doctors (
    id UUID PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    hospital VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    years_of_experience INTEGER,
    role VARCHAR(20) DEFAULT 'DOCTOR',
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### consultations Table
```sql
CREATE TABLE consultations (
    id UUID PRIMARY KEY,
    patient_id UUID NOT NULL,
    worker_id UUID NOT NULL,
    doctor_id UUID NOT NULL,
    visit_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL, -- REQUESTED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    risk_level VARCHAR(20) NOT NULL, -- LOW, HIGH, CRITICAL
    room_id VARCHAR(255),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    doctor_notes TEXT,
    prescription TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (worker_id) REFERENCES anc_workers(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);
```

---

## Frontend Pages

### 1. DOCTOR SIGNUP PAGE (`/doctor/signup`)

**Purpose:** Register new doctors

**Form Fields:**
- Full Name (required)
- Email (required, unique)
- Phone (required, 10 digits)
- Password (required, min 8 chars)
- Specialization (dropdown: Gynecologist, Obstetrician, General Physician)
- License Number (required)
- Hospital/Clinic Name (required)
- District (dropdown)
- Years of Experience (number)

**Design:**
- Same NeoSure theme as ANC worker signup
- Multi-step form (2 steps):
  - Step 1: Personal & Contact Info
  - Step 2: Professional Details
- Frosted glass card on peach background
- Validation with error messages

---

### 2. DOCTOR LOGIN PAGE (`/doctor/login`)

**Purpose:** Doctor authentication

**Form Fields:**
- Email
- Password
- Remember Me checkbox

**Design:**
- Same NeoSure theme as ANC worker login
- Frosted glass card
- Link to signup page
- "Back to Home" link

---

### 3. DOCTOR DASHBOARD HOME (`/doctor/dashboard`)

**Purpose:** Overview of consultations and high-risk cases

**Components:**

#### A. Statistics Cards (Top Row)
- **Pending Requests**
  - API: `GET /api/consultations/pending` → count
  - Icon: Clock
  - Color: Amber
  - Badge: URGENT

- **Today's Consultations**
  - API: `GET /api/consultations/my-consultations` → filter today
  - Icon: Video
  - Color: Terra
  - Badge: TODAY

- **Critical Cases**
  - API: `GET /api/doctor/critical-cases` → count
  - Icon: AlertTriangle
  - Color: Red
  - Badge: CRITICAL

- **Total Consultations**
  - API: `GET /api/consultations/my-consultations` → count
  - Icon: Activity
  - Color: Green
  - Badge: COMPLETED

#### B. Availability Toggle
- **Switch Button:** Online/Offline
- **API:** `PUT /api/auth/doctor/availability`
- **Visual:** Green (Online) / Gray (Offline)
- **Position:** Top-right of dashboard

#### C. Pending Consultation Requests
- **API:** `GET /api/consultations/pending`
- **Display:** Cards with:
  - Patient Name, Age
  - Risk Level Badge (HIGH/CRITICAL)
  - Risk Score
  - ANC Worker Name
  - Request Time
  - Top 3 Warnings
  - Actions: Accept / View Details

#### D. Upcoming Scheduled Consultations
- **API:** `GET /api/consultations/my-consultations` → filter scheduled
- **Display:** Timeline view
- **Each Item:**
  - Scheduled Time
  - Patient Name
  - Risk Level
  - Join Video Call button (if time is near)

#### E. Recent Consultations
- **API:** `GET /api/doctor/recent-consultations`
- **Display:** List of last 5 consultations
- **Each Item:**
  - Patient Name
  - Consultation Date
  - Risk Level
  - Status Badge
  - View Report button

---

### 4. HIGH RISK CASES PAGE (`/doctor/high-risk`)

**Purpose:** View all high-risk and critical pregnancy cases

**Components:**

#### A. Filter Tabs
- All Cases
- Critical Only
- High Risk Only
- Pending Consultation
- Completed

#### B. Case Cards
- **API:** `GET /api/doctor/high-risk-cases` + `/critical-cases`
- **Each Card:**
  - Patient Name, Age, District
  - Risk Level Badge (prominent)
  - Risk Score (large)
  - Gestational Age
  - Last Visit Date
  - Key Warnings (top 3)
  - ANC Worker Contact
  - Actions:
    - Request Consultation
    - View Full Details
    - Call Worker

#### C. Sort Options
- Risk Score (High to Low)
- Most Recent
- Gestational Age

---

### 5. CONSULTATION DETAIL PAGE (`/doctor/consultation/{id}`)

**Purpose:** View complete consultation request details

**Components:**

#### A. Patient Information Card
- Full Name, Age, Blood Group
- Phone, Address, District
- LMP Date, EDD Date, Gestational Age

#### B. Risk Assessment Card
- Risk Level (Large, Prominent)
- Risk Score
- All AI Recommendations
- All AI Warnings

#### C. Visit Data Card
- Vitals (BP, Weight, Temperature, Pulse)
- Lab Reports (Hemoglobin, Blood Sugar, Urine)
- Medical History
- Obstetric History
- Current Symptoms
- Pregnancy Details

#### D. ANC Worker Information
- Worker Name
- Health Center
- Phone Number
- Quick Call button

#### E. Actions
- **Accept Consultation** button
- **Schedule for Later** button (date/time picker)
- **Decline** button (with reason)

---

### 6. VIDEO CONSULTATION PAGE (`/doctor/video/{roomId}`)

**Purpose:** Conduct live video consultation

**Layout:**

#### A. Video Grid
- **Doctor Video:** Large (main view)
- **Patient/Worker Video:** Smaller (picture-in-picture)
- **Controls:**
  - Mute/Unmute Microphone
  - Turn On/Off Camera
  - Screen Share
  - End Call

#### B. Side Panel (Collapsible)
- **Patient Info Tab:**
  - Quick reference to patient details
  - Risk assessment summary
  - Vitals and lab reports

- **Notes Tab:**
  - Real-time note-taking
  - Text area for doctor notes
  - Auto-save every 30 seconds

- **Prescription Tab:**
  - Medication name
  - Dosage
  - Frequency
  - Duration
  - Add multiple medications

- **Recommendations Tab:**
  - Follow-up instructions
  - Lifestyle advice
  - Warning signs to watch
  - Next visit schedule

#### C. Chat Panel
- Text chat with ANC worker
- Share images/documents
- Quick templates for common instructions

#### D. End Consultation Modal
- **Triggers:** When doctor clicks "End Call"
- **Required Fields:**
  - Doctor Notes (summary)
  - Prescription (if any)
  - Recommendations
  - Follow-up required? (Yes/No)
  - Next consultation date (if needed)
- **Actions:**
  - Save & End
  - Cancel (continue call)

---

### 7. CONSULTATION HISTORY PAGE (`/doctor/consultations`)

**Purpose:** View all past consultations

**Components:**

#### A. Statistics
- Total Consultations
- This Month
- Average Duration
- Completion Rate

#### B. Filter & Search
- Search by patient name
- Filter by risk level
- Filter by date range
- Filter by status

#### C. Consultations Table
- **Columns:**
  - Date & Time
  - Patient Name
  - Risk Level Badge
  - Duration
  - Status
  - Actions (View Report)

#### D. Consultation Report Modal
- Patient details
- Risk assessment
- Doctor notes
- Prescription
  - Recommendations
- Consultation duration
- Download PDF button
- Share button

---

### 8. DOCTOR PROFILE PAGE (`/doctor/profile`)

**Purpose:** View and edit doctor profile

**Components:**

#### A. Profile Card
- Profile picture (upload)
- Full Name
- Specialization
- License Number
- Hospital
- District
- Years of Experience
- Email, Phone

#### B. Availability Settings
- Working Hours (time picker)
- Working Days (checkboxes)
- Break Times
- Maximum consultations per day

#### C. Statistics
- Total Consultations
- Average Rating (if implemented)
- Specialization
- Member Since

#### D. Edit Profile Button
- Opens modal with editable fields
- Update API call

---

## Video Consultation Technology

### WebRTC Implementation

**Option 1: Simple Peer (Recommended for MVP)**
```javascript
// Using simple-peer library
import Peer from 'simple-peer';

// Signaling server: Socket.io
// STUN/TURN servers: Free Google STUN servers
```

**Option 2: Daily.co API (Production Ready)**
```javascript
// Using Daily.co prebuilt UI
import DailyIframe from '@daily-co/daily-js';

// Features:
// - Built-in UI
// - Recording
// - Screen sharing
// - Chat
// - Free tier: 10,000 minutes/month
```

**Option 3: Agora SDK (Enterprise)**
```javascript
// Using Agora Web SDK
import AgoraRTC from 'agora-rtc-sdk-ng';

// Features:
// - High quality
// - Low latency
// - Recording
// - Analytics
```

### Recommended: Daily.co for MVP

**Why Daily.co:**
- Easy integration (5 minutes setup)
- Professional UI out of the box
- Free tier sufficient for testing
- Recording capability
- No server infrastructure needed
- HIPAA compliant (for healthcare)

**Implementation:**
```javascript
// Create room (Backend)
POST https://api.daily.co/v1/rooms
Headers: Authorization: Bearer YOUR_API_KEY
Body: { "name": "consultation-{uuid}", "privacy": "private" }

// Join room (Frontend)
const callFrame = DailyIframe.createFrame({
  showLeaveButton: true,
  iframeStyle: {
    width: '100%',
    height: '100%',
    border: '0',
    borderRadius: '12px'
  }
});

callFrame.join({ url: 'https://your-domain.daily.co/consultation-{uuid}' });
```

---

## ANC Worker Integration

### New Features for ANC Worker Dashboard

#### 1. Request Consultation Button
- **Location:** Patient Detail Page, Visit Results Page
- **Condition:** Only show for HIGH/CRITICAL risk
- **Action:** Opens modal to select doctor and schedule

#### 2. Consultation Status Badge
- **Location:** Patient cards, Visit cards
- **States:**
  - REQUESTED (Amber)
  - SCHEDULED (Blue)
  - IN_PROGRESS (Green, pulsing)
  - COMPLETED (Green)
  - CANCELLED (Gray)

#### 3. Join Video Call Button
- **Location:** Consultation detail page
- **Condition:** Only when status is IN_PROGRESS
- **Action:** Opens video call page

#### 4. Consultation Reports
- **Location:** Patient Detail Page → Consultations Tab
- **Display:** List of all consultations for patient
- **Each Item:**
  - Doctor Name
  - Date
  - Doctor Notes
  - Prescription
  - Recommendations
  - Download PDF

---

## Design System (NeoSure Theme)

### Colors (Same as existing)
```css
--terra:     #C4622D
--terra-dk:  #9E4A1E
--peach:     #F5E6D8
--cream:     #FAF4EE
--brown-dk:  #2C1A0E
--green:     #3A7D5C
--amber:     #C4860A
--red:       #C03040
```

### New Components

#### Video Call Container
```css
.video-container {
  background: #1a1a1a;
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
}

.video-main {
  width: 100%;
  aspect-ratio: 16/9;
}

.video-pip {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 200px;
  border-radius: 0.5rem;
  border: 2px solid white;
}
```

#### Consultation Card
```css
.consultation-card {
  background: white;
  border-left: 4px solid var(--terra);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.consultation-card.critical {
  border-left-color: var(--red);
}

.consultation-card.high {
  border-left-color: var(--amber);
}
```

---

## Implementation Priority

### Phase 1: Backend Setup
1. Create Doctor entity and repository
2. Create Consultation entity and repository
3. Implement Doctor authentication
4. Implement Consultation APIs
5. Update Security Config for doctor role

### Phase 2: Doctor Frontend
1. Doctor Signup Page
2. Doctor Login Page
3. Doctor Dashboard Home
4. High Risk Cases Page
5. Consultation Detail Page

### Phase 3: Video Integration
1. Integrate Daily.co API
2. Create Video Consultation Page
3. Implement call controls
4. Add side panel with notes/prescription
5. End consultation flow

### Phase 4: ANC Worker Integration
1. Add "Request Consultation" button
2. Add consultation status badges
3. Add "Join Video Call" functionality
4. Add consultation reports view

### Phase 5: Polish
1. Notifications (real-time)
2. Email notifications
3. SMS notifications
4. PDF report generation
5. Analytics dashboard

---

## Security Considerations

### Authentication
- Separate JWT tokens for doctors
- Role-based access control (RBAC)
- Doctor can only see assigned consultations

### Video Call Security
- Private rooms with unique IDs
- Time-limited access tokens
- End-to-end encryption (WebRTC)
- No recording without consent

### Data Privacy
- HIPAA compliance considerations
- Encrypted data transmission
- Secure storage of medical records
- Audit logs for all actions

---

## API Examples

### Doctor Signup
```json
POST /api/auth/doctor/signup
{
  "fullName": "Dr. Priya Sharma",
  "email": "priya.sharma@hospital.com",
  "phone": "9876543210",
  "password": "SecurePass123",
  "specialization": "Gynecologist",
  "licenseNumber": "MH-12345",
  "hospital": "City Hospital",
  "district": "Mumbai",
  "yearsOfExperience": 10
}
```

### Request Consultation
```json
POST /api/consultations/request
{
  "patientId": "uuid",
  "doctorId": "uuid",
  "visitId": "visit-123",
  "riskLevel": "CRITICAL",
  "scheduledAt": "2024-03-20T10:00:00",
  "notes": "Patient showing severe symptoms"
}
```

### Complete Consultation
```json
PUT /api/consultations/{id}/complete
{
  "doctorNotes": "Patient examined via video consultation...",
  "prescription": "1. Tab Aspirin 75mg - Once daily\n2. Tab Folic Acid 5mg - Once daily",
  "recommendations": "1. Bed rest for 2 days\n2. Follow-up in 1 week\n3. Monitor blood pressure daily"
}
```

---

This specification provides everything needed to implement a complete Doctor Dashboard with Video Consultation capability integrated with your existing ANC system.

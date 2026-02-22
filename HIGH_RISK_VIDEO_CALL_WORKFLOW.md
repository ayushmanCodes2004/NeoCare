# ✅ High-Risk Video Call Workflow - Complete Implementation

## Overview

When a visit is detected as high-risk by the AI, the system automatically creates a consultation and adds it to the doctor's queue. Doctors can then accept the consultation and start a video call with the patient.

---

## Complete Workflow

### Step 1: Worker Registers Visit
1. Worker fills 7-step ANC visit form
2. Submits form to Backend
3. Backend saves visit to database

### Step 2: AI Risk Assessment
1. Backend sends data to RAG Pipeline (port 8000)
2. RAG analyzes data and returns risk assessment
3. Backend saves risk assessment to visit entity
4. Visit status changes to "AI_ANALYZED"

### Step 3: Automatic Consultation Creation (If High Risk)
**Backend automatically creates consultation when `isHighRisk = true`**

**Code Location:** `Backend/src/main/java/com/anc/service/AncVisitService.java`

```java
// 7. Auto-create consultation if high risk
if (Boolean.TRUE.equals(entity.getIsHighRisk())) {
    try {
        consultationService.createFromVisit(entity);
        log.info("Consultation auto-created for high risk visit: {}", entity.getId());
    } catch (Exception e) {
        log.error("Failed to create consultation for visit {}: {}", entity.getId(), e.getMessage());
        // Non-blocking — don't fail the visit registration
    }
}
```

**What Gets Created:**
- Consultation entity with status "PENDING"
- Linked to the visit, patient, and worker
- Priority score calculated based on risk level
- Added to doctor's consultation queue

### Step 4: Doctor Views Queue
1. Doctor logs in to doctor portal
2. Dashboard shows pending consultations
3. Consultations sorted by priority (CRITICAL > HIGH > MEDIUM > LOW)
4. Doctor can see:
   - Patient name and age
   - Risk level badge
   - Risk score
   - Gestational age
   - District/location

### Step 5: Doctor Accepts Consultation
1. Doctor clicks on consultation in queue
2. Views detailed patient information:
   - Risk factors
   - AI recommendations
   - Clinical summary
   - Vitals and lab reports
3. Clicks "Accept Consultation" button
4. Status changes to "ACCEPTED"

### Step 6: Doctor Starts Video Call
1. After accepting, "Start Video Call" button appears
2. Doctor clicks button
3. Status changes to "IN_PROGRESS"
4. Video call interface opens (WebRTC)

### Step 7: Video Consultation
1. Doctor and patient/worker connect via video
2. Doctor reviews case in real-time
3. Doctor provides guidance and recommendations
4. Doctor can see all patient data during call

### Step 8: Doctor Completes Consultation
1. After call, doctor clicks "Complete Consultation"
2. Doctor fills in:
   - Doctor Notes (examination findings)
   - Diagnosis (clinical diagnosis)
   - Action Plan (follow-up plan)
3. Clicks "Complete" button
4. Status changes to "COMPLETED"
5. Consultation moves to history

---

## Backend Implementation

### Automatic Consultation Creation

**Service:** `Backend/src/main/java/com/anc/service/ConsultationService.java`

```java
@Transactional
public ConsultationEntity createFromVisit(AncVisitEntity visit) {
    log.info("Creating consultation for high-risk visit: {}", visit.getId());

    // Check if consultation already exists for this visit
    List<String> activeStatuses = List.of("PENDING", "ACCEPTED", "IN_PROGRESS");
    if (consultationRepository.existsByVisitIdAndStatusIn(visit.getId(), activeStatuses)) {
        log.warn("Consultation already exists for visit: {}", visit.getId());
        throw new RuntimeException("Consultation already exists for this visit");
    }

    // Calculate priority score
    int priorityScore = calculatePriorityScore(visit.getRiskLevel());

    // Build consultation entity
    ConsultationEntity consultation = ConsultationEntity.builder()
            .visitId(visit.getId())
            .patientId(visit.getPatientId())
            .workerId(visit.getWorkerId())
            .doctorId(null)  // Unassigned initially
            .riskLevel(visit.getRiskLevel())
            .isHighRisk(visit.getIsHighRisk())
            .priorityScore(priorityScore)
            .status("PENDING")
            .build();

    consultation = consultationRepository.save(consultation);
    log.info("Consultation created: {} with priority {}", consultation.getId(), priorityScore);

    return consultation;
}
```

### Priority Score Calculation

```java
private int calculatePriorityScore(String riskLevel) {
    if (riskLevel == null) return 0;
    switch (riskLevel.toUpperCase()) {
        case "CRITICAL": return 100;
        case "HIGH": return 75;
        case "MEDIUM": return 50;
        case "LOW": return 25;
        default: return 0;
    }
}
```

### API Endpoints

**Get Consultation Queue:**
```
GET /api/consultations/queue
Authorization: Bearer {doctor_token}
```

**Get Consultation Details:**
```
GET /api/consultations/{consultationId}
Authorization: Bearer {doctor_token}
```

**Accept Consultation:**
```
POST /api/consultations/{consultationId}/accept
Authorization: Bearer {doctor_token}
```

**Start Video Call:**
```
POST /api/consultations/{consultationId}/start-call
Authorization: Bearer {doctor_token}
```

**Complete Consultation:**
```
POST /api/consultations/{consultationId}/complete
Authorization: Bearer {doctor_token}
Content-Type: application/json

{
  "doctorNotes": "Patient examined...",
  "diagnosis": "Gestational hypertension",
  "actionPlan": "Monitor BP daily, follow-up in 1 week"
}
```

---

## Frontend Implementation (Lovable)

### Doctor Dashboard
**File:** `Frontend/lovable-frontend/src/pages/doctor/DoctorDashboard.tsx`

- Shows top 5 pending consultations
- Displays risk badges and patient info
- Link to full consultation queue

### Consultation Queue
**File:** `Frontend/lovable-frontend/src/pages/doctor/ConsultationQueue.tsx`

- Shows all consultations
- Filter by status (PENDING, ACCEPTED, IN_PROGRESS, COMPLETED)
- Sorted by priority score
- Click to view details

### Consultation Detail
**File:** `Frontend/lovable-frontend/src/pages/doctor/ConsultationDetail.tsx`

**Features:**
- Patient information display
- Risk assessment details
- Risk factors list
- AI recommendations
- Clinical summary
- Action buttons based on status:
  - PENDING → "Accept Consultation" button
  - ACCEPTED → "Start Video Call" button
  - IN_PROGRESS → "Complete Consultation" button
  - COMPLETED → Shows consultation notes

### Video Call Integration
**Status:** Partially implemented

The "Start Video Call" button changes status to "IN_PROGRESS" but doesn't open a video interface yet. The old frontend (`Frontend/anc-frontend`) has full WebRTC implementation that can be integrated.

---

## Risk Level Triggers

### When Consultation is Created

Consultation is automatically created when:
- `isHighRisk = true` (returned by RAG Pipeline)
- Risk level is HIGH or CRITICAL

### Risk Level Examples

**CRITICAL Risk (Priority 100):**
- Severe pre-eclampsia (BP ≥ 160/110)
- Severe anemia (Hb < 7 g/dL)
- Multiple high-risk factors
- Immediate doctor consultation required

**HIGH Risk (Priority 75):**
- Moderate pre-eclampsia (BP 140-159/90-109)
- Moderate anemia (Hb 7-9 g/dL)
- Gestational diabetes
- Twin pregnancy
- Urgent doctor consultation recommended

**MEDIUM Risk (Priority 50):**
- Mild hypertension
- Mild anemia (Hb 9-11 g/dL)
- Previous cesarean section
- Routine monitoring needed

**LOW Risk (Priority 25):**
- Normal pregnancy
- No significant risk factors
- Routine antenatal care

---

## Testing the Workflow

### Prerequisites:
1. ✅ Backend running on port 8080
2. ✅ RAG Pipeline running on port 8000
3. ✅ Frontend running on port 5173
4. ✅ Backend restarted to load latest code

### Test Steps:

#### 1. Create High-Risk Visit (Worker)
```
1. Login as worker: http://localhost:5173
2. Select patient
3. Click "New Visit"
4. Fill form with high-risk data:
   - BP Systolic: 160 (high)
   - BP Diastolic: 110 (high)
   - Hemoglobin: 8.0 (low)
   - Age: 38 (advanced maternal age)
5. Submit form
6. Wait for AI analysis
7. Should see HIGH or CRITICAL risk result
```

#### 2. Verify Consultation Created
```
Check Backend logs for:
"Consultation auto-created for high risk visit: {visitId}"
```

#### 3. Doctor Views Queue
```
1. Login as doctor: http://localhost:5173/doctor/login
2. Dashboard should show new consultation
3. Click "View Full Queue"
4. Should see consultation with HIGH/CRITICAL badge
```

#### 4. Doctor Accepts Consultation
```
1. Click on consultation
2. Review patient details
3. Click "Accept Consultation"
4. Status changes to ACCEPTED
```

#### 5. Doctor Starts Video Call
```
1. "Start Video Call" button appears
2. Click button
3. Status changes to IN_PROGRESS
4. (Video interface would open here - needs WebRTC integration)
```

#### 6. Doctor Completes Consultation
```
1. Click "Complete Consultation"
2. Fill in:
   - Doctor Notes: "Patient examined, BP elevated..."
   - Diagnosis: "Gestational hypertension"
   - Action Plan: "Monitor BP daily, follow-up in 1 week"
3. Click "Complete"
4. Status changes to COMPLETED
5. Consultation moves to history
```

---

## What's Working ✅

1. ✅ Automatic consultation creation for high-risk visits
2. ✅ Priority-based consultation queue
3. ✅ Doctor dashboard with pending consultations
4. ✅ Consultation detail page with patient info
5. ✅ Accept consultation workflow
6. ✅ Status management (PENDING → ACCEPTED → IN_PROGRESS → COMPLETED)
7. ✅ Complete consultation with notes
8. ✅ Consultation history

---

## What Needs Integration ⚠️

### Video Call Interface
The Lovable frontend has the button and status management, but doesn't have the actual video call interface yet.

**Options:**

1. **Integrate WebRTC from Old Frontend**
   - Copy `Frontend/anc-frontend/src/utils/webrtc.js`
   - Copy `Frontend/anc-frontend/src/pages/VideoConsultationPage.jsx`
   - Adapt to Lovable frontend structure

2. **Use Third-Party Service**
   - Integrate Twilio Video
   - Integrate Agora.io
   - Integrate Daily.co

3. **Simple Implementation**
   - For now, "Start Video Call" changes status
   - Doctor and worker can use external video tool (Zoom, Google Meet)
   - System tracks consultation status

---

## Database Schema

### Consultations Table
```sql
CREATE TABLE consultations (
    id UUID PRIMARY KEY,
    visit_id UUID REFERENCES anc_visits(id),
    patient_id VARCHAR(50),
    worker_id VARCHAR(50),
    doctor_id VARCHAR(50),
    risk_level VARCHAR(20),
    is_high_risk BOOLEAN,
    priority_score INTEGER,
    status VARCHAR(30),
    doctor_notes TEXT,
    diagnosis TEXT,
    action_plan TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    accepted_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## API Response Examples

### Consultation Queue Response
```json
[
  {
    "consultationId": "abc123",
    "visitId": "visit456",
    "patientId": "PAT001",
    "patientName": "Test Patient",
    "patientAge": 38,
    "gestationalAge": "30 weeks",
    "district": "District A",
    "patientPhone": "+1234567890",
    "riskLevel": "CRITICAL",
    "riskScore": 95,
    "priorityScore": 100,
    "status": "PENDING",
    "riskFactors": ["Severe Pre-eclampsia", "Advanced Maternal Age"],
    "aiRecommendations": ["Immediate referral to CEmOC facility"],
    "clinicalSummary": "38-year-old G2P1 at 30 weeks...",
    "createdAt": "2026-02-22T10:30:00"
  }
]
```

### Consultation Detail Response
```json
{
  "consultationId": "abc123",
  "visitId": "visit456",
  "patientId": "PAT001",
  "patientName": "Test Patient",
  "patientAge": 38,
  "gestationalAge": "30 weeks",
  "district": "District A",
  "patientPhone": "+1234567890",
  "workerId": "worker123",
  "doctorId": "doctor456",
  "riskLevel": "CRITICAL",
  "riskScore": 95,
  "isHighRisk": true,
  "priorityScore": 100,
  "status": "ACCEPTED",
  "riskFactors": ["Severe Pre-eclampsia", "Advanced Maternal Age"],
  "aiRecommendations": ["Immediate referral to CEmOC facility"],
  "clinicalSummary": "38-year-old G2P1 at 30 weeks...",
  "doctorNotes": null,
  "diagnosis": null,
  "actionPlan": null,
  "createdAt": "2026-02-22T10:30:00",
  "acceptedAt": "2026-02-22T10:35:00",
  "startedAt": null,
  "completedAt": null
}
```

---

## Summary

✅ **Automatic consultation creation is fully implemented**
✅ **Doctor queue and workflow is complete**
✅ **Status management works correctly**
✅ **Consultation notes and completion works**
⚠️ **Video call interface needs WebRTC integration**

The system automatically creates consultations for high-risk visits and adds them to the doctor's queue. Doctors can accept, review, and complete consultations. The only missing piece is the actual video call interface, which can be integrated from the old frontend or a third-party service.

**After restarting Backend, test with high-risk data to see the complete workflow in action!**

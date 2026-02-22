# 🔴 CRITICAL: Frontend-Backend Field Name Mismatch

## ❌ Root Cause of 422 Error

The Lovable frontend (`frontend-forge`) is sending data with **snake_case** field names, but the Backend DTOs expect **camelCase** field names!

---

## 🔍 Field Name Comparison

### Frontend Sends (snake_case):
```javascript
{
  patient_info: {
    name: "...",
    age: 26,
    gestational_age_weeks: 24,  // ❌ WRONG
    gravida: 2,
    para: 1,
    abortions: 0,
    living_children: 1
  },
  vitals: {
    blood_pressure_systolic: 120,  // ❌ WRONG
    blood_pressure_diastolic: 80,  // ❌ WRONG
    pulse_rate: 78,  // ❌ WRONG
    temperature: 98.6,  // ❌ WRONG
    weight_kg: 65,  // ❌ WRONG
    height_cm: 160,  // ❌ WRONG
    bmi: 25.4,
    respiratory_rate: 18  // ❌ WRONG
  },
  current_symptoms: {
    complaints: ["Mild headache"],  // ❌ WRONG (array)
    severity: "mild",
    duration_days: 2  // ❌ WRONG
  },
  // ... more snake_case fields
}
```

### Backend Expects (camelCase):
```java
{
  patient_info: {
    name: "...",  // ❌ Backend doesn't have this field!
    age: 26,
    gestationalWeeks: 24,  // ✅ camelCase
    gravida: 2,  // ❌ Backend doesn't have this!
    para: 1,  // ❌ Backend doesn't have this!
    // ... Backend only has age and gestationalWeeks!
  },
  vitals: {
    bpSystolic: 120,  // ✅ camelCase
    bpDiastolic: 80,  // ✅ camelCase
    heightCm: 160,  // ✅ camelCase
    bmi: 25.4
    // ❌ Missing: weightKg, pulseRate, etc.
  },
  // ... more camelCase fields
}
```

### RAG Pipeline Expects (camelCase):
```python
{
  patient_info: {
    patientId: "...",
    name: "...",
    age: 26,
    gravida: 2,
    para: 1,
    livingChildren: 1,
    gestationalWeeks: 24,  // ✅ camelCase
    lmpDate: "...",
    estimatedDueDate: "..."
  },
  vitals: {
    weightKg: 65,  // ✅ camelCase
    heightCm: 160,
    bmi: 25.4,
    bpSystolic: 120,
    bpDiastolic: 80,
    pulseRate: 78,
    respiratoryRate: 18,
    temperatureCelsius: 37.0,
    pallor: false,
    pedalEdema: false
  }
}
```

---

## 🎯 The Problem

1. **Frontend** sends snake_case → **Backend** expects camelCase
2. **Backend DTOs** are missing many fields that RAG Pipeline needs
3. **Backend** doesn't transform the data before sending to RAG

---

## ✅ Solution Options

### Option 1: Fix Frontend (Recommended)
Update the Lovable frontend to send camelCase field names matching the backend.

### Option 2: Fix Backend DTOs
Add all missing fields to Backend DTOs and add @JsonProperty annotations for both snake_case and camelCase.

### Option 3: Add Mapper in Backend
Create a mapper service that transforms frontend data to RAG format.

---

## 🔧 Quick Fix: Update Frontend

**File:** `Frontend/lovable-frontend/src/pages/worker/VisitForm.tsx`

Change the `handleSubmit` function to use camelCase:

```typescript
const body = {
  patientId,
  patientName: form.patientName,
  workerId: user?.workerId,
  phcId: 'PHC-001',
  structured_data: {
    patient_info: {
      patientId: patientId,  // ADD
      name: form.patientName,
      age: parseInt(form.age) || 0,
      gravida: parseInt(form.gravida) || 0,
      para: parseInt(form.para) || 0,
      livingChildren: parseInt(form.livingChildren) || 0,  // CHANGE from living_children
      gestationalWeeks: parseInt(form.gestationalAge) || 0,  // CHANGE from gestational_age_weeks
      lmpDate: form.lmpDate,  // ADD
      estimatedDueDate: form.eddDate  // ADD
    },
    vitals: {
      weightKg: w,  // CHANGE from weight_kg
      heightCm: h,  // CHANGE from height_cm
      bmi: bmi,
      bpSystolic: parseInt(form.bpSystolic) || 0,  // CHANGE from blood_pressure_systolic
      bpDiastolic: parseInt(form.bpDiastolic) || 0,  // CHANGE from blood_pressure_diastolic
      pulseRate: parseInt(form.pulse) || 0,  // CHANGE from pulse_rate
      respiratoryRate: parseInt(form.respRate) || 0,  // CHANGE from respiratory_rate
      temperatureCelsius: parseFloat(form.temp) || 0,  // CHANGE from temperature
      pallor: false,  // ADD
      pedalEdema: false  // ADD
    },
    medical_history: {
      previousLSCS: false,  // ADD
      badObstetricHistory: false,  // ADD
      previousStillbirth: false,  // ADD
      previousPretermDelivery: false,  // ADD
      previousAbortion: parseInt(form.abortions) > 0,  // ADD
      systemicIllness: form.chronicConditions || "None",  // ADD
      chronicHypertension: false,  // ADD
      diabetes: false,  // ADD
      thyroidDisorder: false,  // ADD
      smoking: false,  // ADD
      tobaccoUse: false,  // ADD
      alcoholUse: false  // ADD
    },
    lab_reports: {
      hemoglobin: parseFloat(form.hemoglobin) || 0,
      plateletCount: null,  // ADD
      bloodGroup: form.bloodGroup,  // CHANGE from blood_group
      rhNegative: false,  // ADD
      urineProtein: form.urineProtein === 'Positive',  // CHANGE from string to boolean
      urineSugar: false,  // ADD
      fastingBloodSugar: parseFloat(form.bloodSugar) || null,  // CHANGE from blood_sugar_fasting
      ogtt2hrPG: null,  // ADD
      hivPositive: form.hivStatus === 'Positive',  // CHANGE from string to boolean
      syphilisPositive: false,  // ADD
      serumCreatinine: null,  // ADD
      ast: null,  // ADD
      alt: null  // ADD
    },
    obstetric_history: {
      birthOrder: null,  // ADD
      interPregnancyInterval: null,  // ADD
      stillbirthCount: 0,  // ADD
      abortionCount: parseInt(form.abortions) || 0,  // ADD
      pretermHistory: false  // ADD
    },
    pregnancy_details: {
      twinPregnancy: false,  // ADD
      malpresentation: false,  // ADD
      placentaPrevia: false,  // ADD
      reducedFetalMovement: false,  // ADD
      amnioticFluidNormal: true,  // ADD
      umbilicalDopplerAbnormal: false  // ADD
    },
    current_symptoms: {
      headache: form.complaints.toLowerCase().includes('headache'),  // CHANGE from array
      visualDisturbance: false,  // ADD
      epigastricPain: false,  // ADD
      decreasedUrineOutput: false,  // ADD
      bleedingPerVagina: false,  // ADD
      convulsions: false  // ADD
    }
  }
};
```

---

## 📋 Complete Field Mapping Table

| Frontend Field | Backend DTO Field | RAG Pipeline Field | Status |
|----------------|-------------------|-------------------|--------|
| `gestational_age_weeks` | `gestationalWeeks` | `gestationalWeeks` | ❌ Mismatch |
| `blood_pressure_systolic` | `bpSystolic` | `bpSystolic` | ❌ Mismatch |
| `blood_pressure_diastolic` | `bpDiastolic` | `bpDiastolic` | ❌ Mismatch |
| `pulse_rate` | ❌ Missing | `pulseRate` | ❌ Missing |
| `temperature` | ❌ Missing | `temperatureCelsius` | ❌ Missing |
| `weight_kg` | ❌ Missing | `weightKg` | ❌ Missing |
| `height_cm` | `heightCm` | `heightCm` | ⚠️ Partial |
| `respiratory_rate` | ❌ Missing | `respiratoryRate` | ❌ Missing |
| `living_children` | ❌ Missing | `livingChildren` | ❌ Missing |
| `duration_days` | ❌ Missing | N/A | ❌ Missing |
| `blood_sugar_fasting` | ❌ Missing | `fastingBloodSugar` | ❌ Missing |

---

## 🚀 Implementation Steps

### Step 1: Update Frontend VisitForm.tsx
Replace the entire `handleSubmit` function with the corrected version above.

### Step 2: Add Missing Fields to Backend DTOs
Update all DTOs to include missing fields (see `ENTITY_MAPPING_MISMATCH_FIX.md`).

### Step 3: Test
1. Fill out the visit form in frontend
2. Submit
3. Check backend logs for the JSON being sent
4. Verify RAG Pipeline returns 200 instead of 422

---

## 🐛 Debugging

### Check Frontend Payload
Open browser DevTools → Network tab → Find the POST request to `/api/anc/register-visit` → Check the request payload.

### Check Backend Logs
Look for: `"FastAPI Request: {...}"` in Terminal 2 to see what's being sent to RAG.

### Check RAG Pipeline Logs
Look for validation errors in Terminal 4 after the 422 response.

---

## ✅ Expected Result

After fixing, you should see:
```
INFO: 127.0.0.1:xxxxx - "POST /assess-structured HTTP/1.1" 200 OK
```

Instead of:
```
INFO: 127.0.0.1:xxxxx - "POST /assess-structured HTTP/1.1" 422 Unprocessable Content
```

---

This is the root cause of your 422 error! The field names don't match between frontend, backend, and RAG Pipeline.

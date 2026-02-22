# 🐛 Debugging the 422 Error

## Current Status
You're getting a 422 error when submitting the visit form, which means the RAG Pipeline is rejecting the data due to validation errors.

## Root Cause
The frontend (VisitForm.tsx) was fixed to send correct field names, but your browser may still be using the old cached version.

## Quick Fix Steps

### Step 1: Hard Refresh the Frontend
1. Open http://localhost:5173 in your browser
2. Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac) to hard refresh
3. Or press `F12` to open DevTools, then right-click the refresh button and select "Empty Cache and Hard Reload"

### Step 2: Test the Form Again
1. Login as worker
2. Select a patient
3. Click "Register New Visit"
4. Fill all 7 steps with test data:
   - **Step 1 (Patient Info):** Name, Age: 26, Gestational Age: 24, Gravida: 2, Para: 1, Abortions: 0, Living Children: 1
   - **Step 2 (Vitals):** BP: 120/80, Pulse: 78, Temp: 98.6, Weight: 65, Height: 160, Resp Rate: 18
   - **Step 3 (Symptoms):** Complaints: "Mild headache", Severity: Mild, Duration: 2
   - **Step 4 (Obstetric History):** Fill with any values or leave blank
   - **Step 5 (Medical History):** Chronic Conditions: "None", leave others blank
   - **Step 6 (Pregnancy):** LMP Date, EDD Date, Current GA: "24 weeks"
   - **Step 7 (Lab Reports):** Hemoglobin: 11.5, Blood Group: O+, Blood Sugar: 90, Urine Protein: Negative, HIV: Negative
5. Click "Submit & Get AI Analysis"

### Step 3: Check the Logs

#### Frontend (Browser Console - F12)
Look for the POST request to `/api/anc/register-visit`
- Click on the request
- Go to "Payload" tab
- Verify field names are camelCase (not snake_case)

#### Backend (Terminal 2)
Look for:
```
FastAPI Request: {...}
```
This shows what's being sent to RAG Pipeline

#### RAG Pipeline (Terminal 4)
Look for:
```
INFO: 127.0.0.1:xxxxx - "POST /assess-structured HTTP/1.1" 200 OK
```
If you see 422, it will show validation errors

---

## Expected Data Format

The RAG Pipeline expects this exact structure:

```json
{
  "clinical_summary": "Auto-generated summary",
  "structured_data": {
    "patient_info": {
      "patientId": "...",
      "name": "...",
      "age": 26,
      "gravida": 2,
      "para": 1,
      "livingChildren": 1,
      "gestationalWeeks": 24,
      "lmpDate": "2024-06-01",
      "estimatedDueDate": "2025-03-01"
    },
    "vitals": {
      "weightKg": 65.0,
      "heightCm": 160.0,
      "bmi": 25.4,
      "bpSystolic": 120,
      "bpDiastolic": 80,
      "pulseRate": 78,
      "respiratoryRate": 18,
      "temperatureCelsius": 37.0,
      "pallor": false,
      "pedalEdema": false
    },
    "medical_history": {
      "previousLSCS": false,
      "badObstetricHistory": false,
      "previousStillbirth": false,
      "previousPretermDelivery": false,
      "previousAbortion": false,
      "systemicIllness": "None",
      "chronicHypertension": false,
      "diabetes": false,
      "thyroidDisorder": false,
      "smoking": false,
      "tobaccoUse": false,
      "alcoholUse": false
    },
    "lab_reports": {
      "hemoglobin": 11.5,
      "plateletCount": null,
      "bloodGroup": "O+",
      "rhNegative": false,
      "urineProtein": false,
      "urineSugar": false,
      "fastingBloodSugar": 90.0,
      "ogtt2hrPG": null,
      "hivPositive": false,
      "syphilisPositive": false,
      "serumCreatinine": null,
      "ast": null,
      "alt": null
    },
    "obstetric_history": {
      "birthOrder": null,
      "interPregnancyInterval": null,
      "stillbirthCount": 0,
      "abortionCount": 0,
      "pretermHistory": false
    },
    "pregnancy_details": {
      "twinPregnancy": false,
      "malpresentation": false,
      "placentaPrevia": false,
      "reducedFetalMovement": false,
      "amnioticFluidNormal": true,
      "umbilicalDopplerAbnormal": false
    },
    "current_symptoms": {
      "headache": false,
      "visualDisturbance": false,
      "epigastricPain": false,
      "decreasedUrineOutput": false,
      "bleedingPerVagina": false,
      "convulsions": false
    }
  }
}
```

---

## Common Issues

### Issue 1: Snake_case field names
**Problem:** Frontend sending `gestational_age_weeks` instead of `gestationalWeeks`
**Fix:** Hard refresh browser (Ctrl+Shift+R)

### Issue 2: Missing required fields
**Problem:** RAG Pipeline requires `age`, `bpSystolic`, `bpDiastolic`, `hemoglobin`
**Fix:** Fill these fields in the form

### Issue 3: Wrong data types
**Problem:** Sending string "Positive" instead of boolean true for `urineProtein`
**Fix:** Already fixed in VisitForm.tsx, just refresh browser

### Issue 4: Browser cache
**Problem:** Browser using old JavaScript code
**Fix:** Clear cache and hard reload

---

## Verification Checklist

After submitting the form, verify:

- [ ] Browser console shows POST request with camelCase fields
- [ ] Backend logs show "FastAPI Request" with correct data
- [ ] RAG Pipeline logs show "200 OK" instead of "422"
- [ ] Frontend redirects to `/worker/visits/{visitId}/result`
- [ ] Result page shows risk assessment with:
  - [ ] Risk Level badge (LOW/MEDIUM/HIGH/CRITICAL)
  - [ ] Risk Score (0-100)
  - [ ] Risk Factors list
  - [ ] Recommendations
  - [ ] Doctor consultation requirement

---

## If Still Getting 422

### Option 1: Check Browser DevTools
1. Open DevTools (F12)
2. Go to Network tab
3. Submit form
4. Find POST to `/api/anc/register-visit`
5. Check "Payload" - are field names camelCase?
6. If NO → Browser cache issue, clear cache
7. If YES → Check backend logs for what's sent to RAG

### Option 2: Check Backend Logs
Look for the exact JSON being sent to RAG Pipeline. If it has snake_case, the backend needs updating.

### Option 3: Test RAG Pipeline Directly
```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -d @test-visit-data.json
```

If this returns 422, the RAG Pipeline will show which field is invalid.

---

## Success Indicators

You'll know it's working when:

1. ✅ No 422 errors in RAG Pipeline logs
2. ✅ Backend logs show "FastAPI responded with HTTP status: 200"
3. ✅ Frontend redirects to result page
4. ✅ Risk assessment displays with HPR (High Pregnancy Risk) if applicable
5. ✅ All risk factors and recommendations shown

---

## Next Steps

1. Hard refresh browser (Ctrl+Shift+R)
2. Fill form with test data
3. Submit and check logs
4. If 422 persists, share the browser console payload screenshot
5. If 200 OK, you should see the AI risk assessment!

**The fix is already in place - just need to refresh the browser to use the updated code!**

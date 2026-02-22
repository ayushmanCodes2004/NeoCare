# Fix: Doctor ID Constraint Error

## Problem
When submitting a high-risk visit (after 7 lab tests), the system tried to create a consultation but failed with:
```
ERROR: null value in column "doctor_id" of relation "consultations" violates not-null constraint
```

## Root Cause
The `consultations` table had a NOT NULL constraint on `doctor_id`, but consultations are created in PENDING status without a doctor assigned. The doctor is assigned later when they accept the consultation.

## Solution Applied

### Database Fix
```sql
ALTER TABLE consultations ALTER COLUMN doctor_id DROP NOT NULL;
```

This allows `doctor_id` to be NULL initially.

## How It Should Work

### 1. High-Risk Visit Detected
When RAG Pipeline returns `isHighRisk: true`:
- Visit is saved with status `AI_ANALYZED`
- Consultation is automatically created with:
  - `status: PENDING`
  - `doctor_id: NULL` (no doctor assigned yet)
  - `patient_id`, `worker_id`, `visit_id` populated
  - `risk_level`, `priority_score` from visit

### 2. Doctor Accepts Consultation
When a doctor clicks "Accept" in their queue:
- `doctor_id` is set to the accepting doctor's ID
- `status` changes to `ACCEPTED`
- `accepted_at` timestamp is set
- Video call room is created

### 3. Video Call Starts
- `status` changes to `IN_PROGRESS`
- `call_started_at` timestamp is set

### 4. Consultation Completed
- Doctor submits notes, diagnosis, action plan
- `status` changes to `COMPLETED`
- `completed_at` timestamp is set

## Verification

Test the flow:
1. Create a patient
2. Submit visit with high-risk indicators
3. Check consultation is created with `doctor_id = NULL`
4. Verify no errors

### Query to Check
```sql
SELECT 
    id,
    visit_id,
    patient_id,
    worker_id,
    doctor_id,
    status,
    risk_level,
    created_at
FROM consultations
ORDER BY created_at DESC
LIMIT 5;
```

Expected result for new consultation:
```
doctor_id: NULL
status: PENDING
risk_level: CRITICAL/HIGH/MEDIUM
```

## Files Modified
- Database: `consultations` table - removed NOT NULL constraint from `doctor_id`

## Status
✅ Fixed - Consultations can now be created without a doctor assigned

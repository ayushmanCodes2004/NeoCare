# 🚀 NeoSure - Quick Start for Lovable

## TL;DR - What You're Building

A maternal health web app with:
- **2 user types:** ANC Workers & Doctors
- **Worker flow:** Register patients → Conduct ANC visits → Get AI risk assessment
- **Doctor flow:** Review consultation queue → Video call → Complete with notes
- **Backend:** Spring Boot REST API on `http://localhost:8080`
- **Theme:** Warm terracotta/beige (#C4622D primary, #F5EBE0 background)

---

## 🎨 Design Theme

```css
Primary: #C4622D (terracotta orange)
Background: #F5EBE0 (warm beige)
Text: #2C1A0E (dark brown)
Success: #10B981 | Warning: #F59E0B | Error: #EF4444
```

**Style:** Professional, warm, minimal, clean cards with 8px border radius

---

## 🔐 Authentication

**localStorage keys:**
- `anc_token` - JWT token
- `anc_role` - "WORKER" or "DOCTOR"
- `anc_user` - User profile JSON

**HTTP header:**
```javascript
Authorization: Bearer <token>
```

---

## 📡 Key API Endpoints

### Worker Auth
```
POST /api/auth/signup
POST /api/auth/login
GET  /api/auth/me
```

### Doctor Auth
```
POST /api/doctor/auth/signup
POST /api/doctor/auth/login
GET  /api/doctor/auth/me
```

### Patients
```
POST /api/patients
GET  /api/patients
GET  /api/patients/{id}
```

### ANC Visits
```
POST /api/anc/register-visit
GET  /api/anc/visits/{visitId}
GET  /api/anc/patients/{patientId}/visits
```

### Consultations
```
GET  /api/consultations/queue
GET  /api/consultations/{id}
POST /api/consultations/{id}/accept
POST /api/consultations/{id}/start-call
POST /api/consultations/{id}/complete
GET  /api/consultations/my-history
```

---

## 🗺️ Routes

### Public
- `/` - Landing page
- `/worker/login` - Worker login
- `/worker/signup` - Worker signup
- `/doctor/login` - Doctor login
- `/doctor/signup` - Doctor signup

### Worker (Protected)
- `/worker/dashboard` - Dashboard
- `/worker/patients` - Patient list
- `/worker/patients/new` - Create patient
- `/worker/patients/:id` - Patient details
- `/worker/visits/new?patientId={id}` - Register visit
- `/worker/visits/:visitId/result` - AI risk results

### Doctor (Protected)
- `/doctor/dashboard` - Dashboard
- `/doctor/consultations` - Queue
- `/doctor/consultations/:id` - Details
- `/doctor/consultations/:id/video` - Video call
- `/doctor/history` - History

---

## 📋 Key Data Structures

### Worker Signup
```json
{
  "fullName": "Priya Sharma",
  "phone": "9876543210",
  "email": "priya@health.gov.in",
  "password": "SecurePass123",
  "healthCenter": "PHC Bangalore",
  "district": "Bangalore Urban"
}
```

### Patient Create
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

### ANC Visit (Complex - see full spec for complete structure)
```json
{
  "patientId": "uuid",
  "patientName": "Lakshmi Devi",
  "workerId": "uuid",
  "phcId": "PHC-001",
  "structured_data": {
    "patient_info": { ... },
    "vitals": { ... },
    "current_symptoms": { ... },
    "obstetric_history": { ... },
    "medical_history": { ... },
    "pregnancy_details": { ... },
    "lab_reports": { ... }
  }
}
```

### Risk Assessment Response
```json
{
  "visitId": "uuid",
  "status": "AI_ANALYZED",
  "riskAssessment": {
    "risk_level": "HIGH",
    "risk_score": 75,
    "risk_factors": ["Low hemoglobin", "..."],
    "recommendations": ["Continue iron supplements", "..."],
    "requires_doctor_consultation": true,
    "urgency": "urgent"
  }
}
```

---

## 🎯 Priority Pages

### Must Build First
1. Landing page
2. Worker login/signup
3. Doctor login/signup
4. Worker dashboard
5. Patient list
6. Create patient
7. Register visit form (multi-step)
8. Visit result (AI risk display)
9. Doctor dashboard
10. Consultation queue
11. Consultation detail
12. Complete consultation form

### Build Later
- Video consultation (WebRTC)
- History pages
- Advanced filters

---

## ⚠️ Important Rules

1. **Phone validation:** 10 digits, starts with 6-9
2. **Date format:** YYYY-MM-DD
3. **Token in header:** `Authorization: Bearer <token>`
4. **Handle 401:** Clear localStorage, redirect to `/`
5. **Risk colors:** LOW=green, MEDIUM=amber, HIGH=orange, CRITICAL=red
6. **Loading states:** Show spinner during AI analysis (3-5 seconds)

---

## 🧪 Test With

- **Swagger UI:** http://localhost:8080/swagger-ui/index.html
- **API Tester:** http://localhost:8080/api-tester.html

---

## 📚 Full Documentation

See `LOVABLE_FRONTEND_SPECIFICATION.md` for:
- Complete API reference with examples
- Detailed page requirements
- WebRTC implementation
- Validation rules
- Error handling
- Sample user flows

---

**Backend is running on port 8080. Start building! 🚀**

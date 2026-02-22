# Doctor Module Implementation - Complete Guide

## Overview
This document provides the complete implementation plan for the doctor module as specified in `doctor.md`.

## What Has Been Created

### ✅ Database Schema
- `Backend/src/main/resources/doctor_module_schema.sql` - Complete schema for doctors and consultations tables

### ✅ Entities
- `Backend/src/main/java/com/anc/entity/DoctorEntity.java` - Doctor account entity (implements UserDetails)
- `Backend/src/main/java/com/anc/entity/ConsultationEntity.java` - Consultation request entity

## What Needs to Be Created

### Backend Repositories
Create these files in `Backend/src/main/java/com/anc/repository/`:

1. **DoctorRepository.java** - Methods: findByPhone, existsByPhone, existsByEmail, findByDistrictAndIsAvailableTrueAndIsActiveTrue
2. **ConsultationRepository.java** - Methods: findPriorityQueue, findByDoctorIdOrderByCreatedAtDesc, findByPatientIdOrderByCreatedAtDesc, existsByVisitIdAndStatusIn

### Backend DTOs
Create these files in `Backend/src/main/java/com/anc/dto/`:

1. **DoctorSignupRequestDTO.java** - Fields: fullName, phone, email, password, specialization, hospital, district, registrationNo
2. **DoctorLoginRequestDTO.java** - Fields: phone, password
3. **DoctorAuthResponseDTO.java** - Fields: token, role, doctorId, fullName, phone, email, specialization, hospital, district, registrationNo, isAvailable, message
4. **ConsultationResponseDTO.java** - Complete consultation with patient/worker/doctor/visit data
5. **ConsultationNotesRequestDTO.java** - Fields: doctorNotes, diagnosis, actionPlan

### Backend Services
Create/Update these files in `Backend/src/main/java/com/anc/service/`:

1. **DoctorAuthService.java** - Methods: signup, login
2. **ConsultationService.java** - Methods: createFromVisit, getPriorityQueue, accept, startCall, complete, getDoctorHistory, getPatientConsultations
3. **VideoSessionService.java** - Methods: createRoom, generateToken (Daily.co integration)
4. **UPDATE JwtService.java** - Add generateToken(phone, userId, role) overload, add extractRole() method
5. **UPDATE AncVisitService.java** - Add auto-creation of consultation when isHighRisk=true

### Backend Security
Update these files in `Backend/src/main/java/com/anc/security/`:

1. **UPDATE CustomUserDetailsService.java** - Check both anc_workers and doctors tables
2. **UPDATE SecurityConfig.java** - Add doctor role-based endpoint protection

### Backend Controllers
Create these files in `Backend/src/main/java/com/anc/controller/`:

1. **DoctorAuthController.java** - Endpoints: /api/doctor/auth/signup, /api/doctor/auth/login, /api/doctor/auth/me
2. **ConsultationController.java** - Endpoints: /api/consultations/queue, /api/consultations/{id}, /api/consultations/{id}/accept, /api/consultations/{id}/start-call, /api/consultations/{id}/complete, /api/consultations/my-history, /api/consultations/patient/{patientId}

### Backend Configuration
1. **UPDATE pom.xml** - Add spring-boot-starter-webflux dependency
2. **UPDATE application.yml** - Add Daily.co configuration (api-key, base-url, domain)

### Frontend API Layer
Create these files in `Frontend/anc-frontend/src/api/`:

1. **doctorApi.js** - Functions: doctorSignup, doctorLogin, getDoctorMe
2. **consultationApi.js** - Functions: getPriorityQueue, getConsultation, acceptConsultation, startCall, completeConsultation, getDoctorHistory, getPatientConsultations

### Frontend Context & Hooks
Create these files in `Frontend/anc-frontend/src/`:

1. **context/DoctorAuthContext.jsx** - Doctor authentication state management
2. **hooks/useDoctorAuth.js** - Hook to use doctor auth context
3. **routes/DoctorProtectedRoute.jsx** - Protected route for doctor pages

### Frontend Components
Create these files in `Frontend/anc-frontend/src/components/doctor/`:

1. **DoctorLayout.jsx** - Sidebar layout for doctor portal
2. **ConsultationCard.jsx** - Queue item card component
3. **PriorityBadge.jsx** - CRITICAL/HIGH/MEDIUM badge with urgency styling
4. **VideoRoom.jsx** - Daily.co video embed component

### Frontend Pages
Create these files in `Frontend/anc-frontend/src/pages/doctor/`:

1. **DoctorLoginPage.jsx** - Doctor login form
2. **DoctorSignupPage.jsx** - Doctor registration form
3. **DoctorQueuePage.jsx** - Priority queue dashboard (main doctor page)
4. **ConsultationDetailPage.jsx** - Full consultation detail with patient info
5. **VideoCallPage.jsx** - Video consultation page
6. **DoctorHistoryPage.jsx** - Past consultations

### Frontend Routing
Update `Frontend/anc-frontend/src/App.jsx`:
- Add doctor routes under /doctor/*
- Configure DoctorProtectedRoute wrapper

## Implementation Order

### Phase 1: Backend Foundation (Do First)
1. Run doctor_module_schema.sql to create tables
2. Create DoctorRepository and ConsultationRepository
3. Create all DTOs
4. Update JwtService with role support
5. Update CustomUserDetailsService to check both tables
6. Update SecurityConfig with doctor endpoints

### Phase 2: Backend Services
1. Create DoctorAuthService
2. Create VideoSessionService
3. Create ConsultationService
4. Update AncVisitService to auto-create consultations

### Phase 3: Backend Controllers
1. Create DoctorAuthController
2. Create ConsultationController
3. Test all endpoints with Postman/curl

### Phase 4: Frontend Foundation
1. Create doctorApi.js and consultationApi.js
2. Create DoctorAuthContext and useDoctorAuth hook
3. Create DoctorProtectedRoute

### Phase 5: Frontend Components & Pages
1. Create all doctor components (Layout, Card, Badge, VideoRoom)
2. Create all doctor pages (Login, Signup, Queue, Detail, History)
3. Update App.jsx with doctor routes

### Phase 6: Testing & Integration
1. Test doctor signup/login flow
2. Test consultation creation when visit is high risk
3. Test priority queue display
4. Test video call integration (requires Daily.co API key)
5. Test consultation completion flow

## Key Configuration Requirements

### application.yml
```yaml
daily:
  api-key: "your-daily-co-api-key-here"
  base-url: "https://api.daily.co/v1"
  domain: "your-domain"

doctor:
  auto-assign-district: true
```

### pom.xml
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

### Frontend package.json
```json
{
  "dependencies": {
    "@daily-co/daily-js": "^0.x.x"
  }
}
```

## Testing Checklist

- [ ] Doctor can signup with phone/email/password
- [ ] Doctor can login and receive JWT with role="DOCTOR"
- [ ] High-risk visit auto-creates consultation in PENDING status
- [ ] Doctor sees priority queue sorted by CRITICAL → HIGH → MEDIUM
- [ ] Doctor can accept a consultation (status → ACCEPTED)
- [ ] Doctor can start video call (creates Daily.co room, status → IN_PROGRESS)
- [ ] Doctor can complete consultation with notes (status → COMPLETED)
- [ ] Worker can view consultation history for their patients
- [ ] Role-based access control works (workers can't access doctor endpoints)

## Reference
All implementation details are in `doctor.md` (2728 lines).

This is a STRICT implementation - follow the specifications exactly as written in doctor.md.

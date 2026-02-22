# Doctor Module - Strict Implementation Plan

## Status: IMPLEMENTING FROM doctor.md

This document tracks the strict implementation of the doctor module as specified in doctor.md.

## Implementation Checklist

### Backend - Database Schema
- [ ] Create `doctors` table with all specified fields
- [ ] Create `consultations` table with all specified fields
- [ ] Add indexes as specified
- [ ] Run migration script

### Backend - Entities
- [ ] DoctorEntity.java (implements UserDetails)
- [ ] ConsultationEntity.java
- [ ] Update existing entities if needed

### Backend - Repositories
- [ ] DoctorRepository.java
- [ ] ConsultationRepository.java with custom queries

### Backend - DTOs
- [ ] DoctorSignupRequestDTO.java
- [ ] DoctorLoginRequestDTO.java (uses phone field)
- [ ] DoctorAuthResponseDTO.java
- [ ] ConsultationResponseDTO.java
- [ ] ConsultationNotesRequestDTO.java

### Backend - Services
- [ ] DoctorAuthService.java
- [ ] ConsultationService.java
- [ ] VideoSessionService.java (Daily.co integration)
- [ ] Update JwtService.java to support role parameter
- [ ] Update AncVisitService.java to auto-create consultations

### Backend - Security
- [ ] Update CustomUserDetailsService.java to check both tables
- [ ] Update SecurityConfig.java with doctor role rules
- [ ] Add role-based endpoint protection

### Backend - Controllers
- [ ] DoctorAuthController.java (/api/doctor/auth/*)
- [ ] ConsultationController.java (/api/consultations/*)

### Backend - Configuration
- [ ] Add Daily.co config to application.yml
- [ ] Add spring-boot-starter-webflux dependency to pom.xml

### Frontend - API Layer
- [ ] doctorApi.js (signup, login, getMe)
- [ ] consultationApi.js (queue, accept, startCall, complete)

### Frontend - Context & Hooks
- [ ] DoctorAuthContext.jsx
- [ ] useDoctorAuth.js hook
- [ ] DoctorProtectedRoute.jsx

### Frontend - Components
- [ ] DoctorLayout.jsx (sidebar)
- [ ] ConsultationCard.jsx
- [ ] PriorityBadge.jsx
- [ ] VideoRoom.jsx (Daily.co integration)

### Frontend - Pages
- [ ] DoctorLoginPage.jsx
- [ ] DoctorSignupPage.jsx
- [ ] DoctorQueuePage.jsx (priority queue dashboard)
- [ ] ConsultationDetailPage.jsx
- [ ] VideoCallPage.jsx
- [ ] DoctorHistoryPage.jsx

### Frontend - Routing
- [ ] Add doctor routes to App.jsx
- [ ] Configure protected routes

## Key Implementation Notes

1. **Role Separation**: Both workers and doctors use phone+password, but JWT contains role claim
2. **Priority Queue**: CRITICAL (100) → HIGH (70) → MEDIUM (40), oldest first
3. **Auto-Creation**: When visit.isHighRisk=true, consultation is auto-created
4. **Video Integration**: Daily.co for WebRTC (requires API key)
5. **Status Lifecycle**: PENDING → ACCEPTED → IN_PROGRESS → COMPLETED

## Current Status
Starting implementation...

# Doctor Module — Complete Implementation
## Doctor Auth + Priority Queue + Video Teleconsultation

**Integrates with:** existing `com.anc` Spring Boot + React ANC Portal

---

## What This Builds

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         FULL DOCTOR FLOW                                 │
│                                                                          │
│  ANC Worker submits visit → FastAPI returns isHighRisk=true              │
│         ↓                                                                │
│  System auto-creates a Consultation Request (status=PENDING)             │
│  Assigned to available doctor in same district                           │
│         ↓                                                                │
│  Doctor logs in → sees Priority Queue                                    │
│    CRITICAL cases at top → HIGH → MEDIUM                                 │
│         ↓                                                                │
│  Doctor clicks "Start Teleconsultation"                                  │
│    → WebRTC video call opens in browser                                  │
│    → ANC Worker gets notified to join                                    │
│         ↓                                                                │
│  Doctor reviews: patient info, vitals, lab reports,                      │
│    AI risk explanation, detected risks                                   │
│         ↓                                                                │
│  Doctor submits consultation notes → status=COMPLETED                    │
│  Worker sees doctor's notes on patient page                              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## New Project Structure (additions only)

```
com.anc/
│
├── entity/
│   ├── (existing entities)
│   ├── DoctorEntity.java                ← NEW: doctor account (implements UserDetails)
│   └── ConsultationEntity.java          ← NEW: consultation request + video session
│
├── repository/
│   ├── (existing repositories)
│   ├── DoctorRepository.java            ← NEW
│   └── ConsultationRepository.java      ← NEW
│
├── dto/
│   ├── (existing DTOs)
│   ├── DoctorSignupRequestDTO.java      ← NEW
│   ├── DoctorLoginRequestDTO.java       ← NEW
│   ├── DoctorAuthResponseDTO.java       ← NEW
│   ├── ConsultationResponseDTO.java     ← NEW
│   └── ConsultationNotesRequestDTO.java ← NEW
│
├── service/
│   ├── (existing services)
│   ├── DoctorAuthService.java           ← NEW: doctor signup + login
│   ├── ConsultationService.java         ← NEW: create, queue, assign, complete
│   └── VideoSessionService.java         ← NEW: generate room tokens (Daily.co)
│
├── controller/
│   ├── (existing controllers)
│   ├── DoctorAuthController.java        ← NEW: /api/doctor/auth/*
│   └── ConsultationController.java      ← NEW: /api/consultations/*
│
└── security/
    └── CustomUserDetailsService.java    ← UPDATE: load BOTH worker AND doctor by phone
```

---

## How Role Separation Works

```
Both ANC Workers and Doctors log in with phone + password.
JWT contains a "role" claim:  "WORKER" or "DOCTOR"

Signup endpoints are separate:
  POST /api/auth/signup        → creates ANC Worker (role=WORKER)
  POST /api/doctor/auth/signup → creates Doctor     (role=DOCTOR)

JwtService.generateToken() now takes role as a parameter.
CustomUserDetailsService checks BOTH tables:
  1. AncWorkerRepository.findByPhone()
  2. DoctorRepository.findByPhone()
```

---

## API Endpoints — Doctor Module

| Method | URL | Role | Description |
|--------|-----|------|-------------|
| POST | `/api/doctor/auth/signup` | ❌ | Doctor registers |
| POST | `/api/doctor/auth/login` | ❌ | Doctor logs in |
| GET | `/api/doctor/auth/me` | DOCTOR | Doctor profile |
| GET | `/api/consultations/queue` | DOCTOR | Priority queue (CRITICAL first) |
| GET | `/api/consultations/{id}` | DOCTOR | Full consultation + patient + visit data |
| POST | `/api/consultations/{id}/accept` | DOCTOR | Doctor accepts the case |
| POST | `/api/consultations/{id}/start-call` | DOCTOR | Generate video room token |
| POST | `/api/consultations/{id}/complete` | DOCTOR | Submit notes, close consultation |
| GET | `/api/consultations/my-history` | DOCTOR | Doctor's past consultations |
| GET | `/api/consultations/patient/{patientId}` | WORKER | Worker sees consultations for their patient |

---

## Consultation Lifecycle

```
visit.isHighRisk = true
       ↓
ConsultationEntity created automatically in AncVisitService
  status    = PENDING
  priority  = visit.riskLevel  (CRITICAL / HIGH / MEDIUM)
  doctorId  = null (unassigned)
       ↓
Doctor opens queue → sorted by priority + createdAt
       ↓
Doctor clicks Accept
  status    = ACCEPTED
  doctorId  = authenticatedDoctor.id
  acceptedAt = now()
       ↓
Doctor clicks Start Call
  VideoSessionService.createRoom(consultationId) → Daily.co API
  status    = IN_PROGRESS
  roomUrl   = "https://anc.daily.co/consult-uuid"
  workerToken, doctorToken generated
       ↓
Doctor submits notes
  status    = COMPLETED
  completedAt = now()
  doctorNotes = "..." saved to DB
```

---

## schema.sql — New Tables

```sql
-- ─── Doctor accounts ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255)    NOT NULL,
    phone           VARCHAR(15)     NOT NULL UNIQUE,
    email           VARCHAR(255)    UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    specialization  VARCHAR(255)    DEFAULT 'Obstetrics & Gynaecology',
    hospital        VARCHAR(255),
    district        VARCHAR(255),
    registration_no VARCHAR(100),               -- medical council reg number
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    is_available    BOOLEAN         NOT NULL DEFAULT TRUE, -- online/offline toggle
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_doctor_phone    ON doctors(phone);
CREATE INDEX        idx_doctor_district ON doctors(district);
CREATE INDEX        idx_doctor_available ON doctors(is_available);

-- ─── Consultation requests ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consultations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Linked records
    visit_id        VARCHAR(255)    NOT NULL,  -- → anc_visits.id
    patient_id      VARCHAR(255)    NOT NULL,  -- → patients.id
    worker_id       VARCHAR(255)    NOT NULL,  -- → anc_workers.id
    doctor_id       VARCHAR(255),              -- → doctors.id (null until accepted)

    -- Risk info (copied from visit for quick sorting)
    risk_level      VARCHAR(20)     NOT NULL,  -- CRITICAL / HIGH / MEDIUM
    is_high_risk    BOOLEAN         NOT NULL DEFAULT TRUE,
    priority_score  INTEGER         NOT NULL DEFAULT 0,
                                               -- CRITICAL=100, HIGH=70, MEDIUM=40

    -- Status lifecycle
    status          VARCHAR(30)     NOT NULL DEFAULT 'PENDING',
                                               -- PENDING/ACCEPTED/IN_PROGRESS/COMPLETED/CANCELLED

    -- Video call
    room_url        VARCHAR(500),              -- Daily.co room URL
    doctor_token    TEXT,                      -- Daily.co token for doctor
    worker_token    TEXT,                      -- Daily.co token for worker

    -- Doctor's notes (filled on completion)
    doctor_notes    TEXT,
    diagnosis       TEXT,
    action_plan     TEXT,

    -- Timestamps
    accepted_at     TIMESTAMP,
    call_started_at TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consult_doctor_id   ON consultations(doctor_id);
CREATE INDEX idx_consult_visit_id    ON consultations(visit_id);
CREATE INDEX idx_consult_patient_id  ON consultations(patient_id);
CREATE INDEX idx_consult_worker_id   ON consultations(worker_id);
CREATE INDEX idx_consult_status      ON consultations(status);
CREATE INDEX idx_consult_priority    ON consultations(priority_score DESC, created_at ASC);
```

---

## pom.xml — Add (if not already present)

```xml
<!-- HTTP client for Daily.co API calls -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>

<!-- Already present — confirming needed -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.3</version>
</dependency>
```

---

## application.yml — Add Video + Doctor Config

```yaml
# Add to existing application.yml

daily:
  api-key: "your-daily-co-api-key-here"       # get free key at daily.co
  base-url: "https://api.daily.co/v1"
  domain: "your-domain"                        # e.g. "anc-portal"

doctor:
  auto-assign-district: true                   # assign to doctor in same district
```

---

## entity/DoctorEntity.java

```java
package com.anc.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

/**
 * Doctor account entity.
 *
 * Implements UserDetails — same pattern as AncWorkerEntity.
 * Login identifier: phone number (unique across ALL users — workers + doctors)
 * Role: "ROLE_DOCTOR" returned in getAuthorities()
 *
 * isAvailable: doctor can toggle ON/OFF to accept consultations.
 */
@Entity
@Table(name = "doctors")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DoctorEntity implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    /** Phone = unique login identifier across the entire system */
    @Column(name = "phone", nullable = false, unique = true, length = 15)
    private String phone;

    @Column(name = "email", unique = true)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    /** e.g. "Obstetrics & Gynaecology" */
    @Column(name = "specialization")
    private String specialization;

    @Column(name = "hospital")
    private String hospital;

    @Column(name = "district")
    private String district;

    /** Medical council registration number */
    @Column(name = "registration_no", length = 100)
    private String registrationNo;

    /** Account active flag — false blocks login */
    @Column(name = "is_active")
    @Builder.Default
    private Boolean isActive = true;

    /** Availability toggle — false means doctor won't receive new consultations */
    @Column(name = "is_available")
    @Builder.Default
    private Boolean isAvailable = true;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // ─── UserDetails ──────────────────────────────────────────────────────────

    /** ROLE_DOCTOR — used by SecurityConfig to restrict doctor-only endpoints */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_DOCTOR"));
    }

    @Override
    public String getPassword() { return passwordHash; }

    @Override
    public String getUsername() { return phone; }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return Boolean.TRUE.equals(isActive); }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return Boolean.TRUE.equals(isActive); }
}
```

---

## entity/ConsultationEntity.java

```java
package com.anc.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * Consultation request — created automatically when a visit is high risk.
 *
 * Links: visit → patient → worker → doctor
 * Tracks: status lifecycle, video call URLs/tokens, doctor's notes.
 *
 * Priority queue: ORDER BY priority_score DESC, created_at ASC
 *   CRITICAL = 100 (shown first)
 *   HIGH     = 70
 *   MEDIUM   = 40
 */
@Entity
@Table(name = "consultations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConsultationEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private String id;

    // ─── Linked records ───────────────────────────────────────────────────────
    @Column(name = "visit_id", nullable = false)
    private String visitId;

    @Column(name = "patient_id", nullable = false)
    private String patientId;

    @Column(name = "worker_id", nullable = false)
    private String workerId;

    /** Null until a doctor accepts the consultation */
    @Column(name = "doctor_id")
    private String doctorId;

    // ─── Risk info (copied from visit) ────────────────────────────────────────
    @Column(name = "risk_level", nullable = false, length = 20)
    private String riskLevel;

    @Column(name = "is_high_risk")
    private Boolean isHighRisk;

    /**
     * Numeric priority for ORDER BY:
     *   CRITICAL = 100, HIGH = 70, MEDIUM = 40
     */
    @Column(name = "priority_score")
    private Integer priorityScore;

    // ─── Status lifecycle ─────────────────────────────────────────────────────
    /**
     * PENDING    → waiting for a doctor to accept
     * ACCEPTED   → doctor accepted, video call not yet started
     * IN_PROGRESS→ video call active
     * COMPLETED  → doctor submitted notes
     * CANCELLED  → worker or system cancelled
     */
    @Column(name = "status", nullable = false, length = 30)
    @Builder.Default
    private String status = "PENDING";

    // ─── Video call (Daily.co) ────────────────────────────────────────────────
    /** Daily.co room URL e.g. "https://anc.daily.co/consult-uuid" */
    @Column(name = "room_url", length = 500)
    private String roomUrl;

    /** Meeting token for doctor — passed to Daily.co JS SDK */
    @Column(name = "doctor_token", columnDefinition = "TEXT")
    private String doctorToken;

    /** Meeting token for ANC worker — passed via notification */
    @Column(name = "worker_token", columnDefinition = "TEXT")
    private String workerToken;

    // ─── Doctor's notes (filled on COMPLETED) ────────────────────────────────
    @Column(name = "doctor_notes", columnDefinition = "TEXT")
    private String doctorNotes;

    @Column(name = "diagnosis", columnDefinition = "TEXT")
    private String diagnosis;

    @Column(name = "action_plan", columnDefinition = "TEXT")
    private String actionPlan;

    // ─── Timestamps ───────────────────────────────────────────────────────────
    @Column(name = "accepted_at")
    private LocalDateTime acceptedAt;

    @Column(name = "call_started_at")
    private LocalDateTime callStartedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

---

## repository/DoctorRepository.java

```java
package com.anc.repository;

import com.anc.entity.DoctorEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DoctorRepository extends JpaRepository<DoctorEntity, String> {

    Optional<DoctorEntity> findByPhone(String phone);

    boolean existsByPhone(String phone);

    boolean existsByEmail(String email);

    /** Find available doctors in the same district for auto-assignment */
    List<DoctorEntity> findByDistrictAndIsAvailableTrueAndIsActiveTrue(String district);

    /** All available doctors (fallback if no district match) */
    List<DoctorEntity> findByIsAvailableTrueAndIsActiveTrue();
}
```

---

## repository/ConsultationRepository.java

```java
package com.anc.repository;

import com.anc.entity.ConsultationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ConsultationRepository extends JpaRepository<ConsultationEntity, String> {

    /**
     * Doctor's priority queue:
     * PENDING + ACCEPTED cases, CRITICAL first, oldest first within same priority.
     * Doctor sees this on their dashboard.
     */
    @Query("""
        SELECT c FROM ConsultationEntity c
        WHERE c.status IN ('PENDING', 'ACCEPTED')
        ORDER BY c.priorityScore DESC, c.createdAt ASC
        """)
    List<ConsultationEntity> findPriorityQueue();

    /**
     * Queue filtered by doctor's district (preferred).
     * Used when auto-assign-district = true.
     */
    @Query("""
        SELECT c FROM ConsultationEntity c
        JOIN PatientEntity p ON c.patientId = p.id
        WHERE c.status IN ('PENDING', 'ACCEPTED')
          AND p.district = :district
        ORDER BY c.priorityScore DESC, c.createdAt ASC
        """)
    List<ConsultationEntity> findPriorityQueueByDistrict(@Param("district") String district);

    /** All consultations assigned to a specific doctor */
    List<ConsultationEntity> findByDoctorIdOrderByCreatedAtDesc(String doctorId);

    /** Active consultation (IN_PROGRESS) for a doctor — at most one at a time */
    Optional<ConsultationEntity> findByDoctorIdAndStatus(String doctorId, String status);

    /** All consultations for a patient — worker uses this to see history */
    List<ConsultationEntity> findByPatientIdOrderByCreatedAtDesc(String patientId);

    /** Check if a pending consultation already exists for this visit */
    boolean existsByVisitIdAndStatusIn(String visitId, List<String> statuses);

    /** CRITICAL count for dashboard */
    @Query("SELECT COUNT(c) FROM ConsultationEntity c WHERE c.riskLevel = 'CRITICAL' AND c.status = 'PENDING'")
    long countPendingCritical();
}
```

---

## dto/DoctorSignupRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Doctor signup request:
 * {
 *   "fullName":       "Dr. Priya Sharma",
 *   "phone":          "9988776655",
 *   "email":          "priya@hospital.in",
 *   "password":       "SecurePass123",
 *   "specialization": "Obstetrics & Gynaecology",
 *   "hospital":       "District Hospital Bangalore Rural",
 *   "district":       "Bangalore Rural",
 *   "registrationNo": "KA-12345"
 * }
 */
@Data
public class DoctorSignupRequestDTO {

    @NotBlank(message = "Full name is required")
    @JsonProperty("fullName")
    private String fullName;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[6-9]\\d{9}$", message = "Enter a valid 10-digit Indian mobile number")
    @JsonProperty("phone")
    private String phone;

    @Email(message = "Enter a valid email address")
    @JsonProperty("email")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    @JsonProperty("password")
    private String password;

    @JsonProperty("specialization")
    private String specialization;

    @NotBlank(message = "Hospital name is required")
    @JsonProperty("hospital")
    private String hospital;

    @NotBlank(message = "District is required")
    @JsonProperty("district")
    private String district;

    @JsonProperty("registrationNo")
    private String registrationNo;
}
```

---

## dto/DoctorLoginRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

/**
 * { "phone": "9988776655", "password": "SecurePass123" }
 */
@Data
public class DoctorLoginRequestDTO {

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[6-9]\\d{9}$", message = "Enter a valid 10-digit Indian mobile number")
    @JsonProperty("phone")
    private String phone;

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    private String password;
}
```

---

## dto/DoctorAuthResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

/**
 * Returned to React after doctor signup/login.
 * role = "DOCTOR" — React uses this to show the doctor portal UI.
 */
@Data
@Builder
public class DoctorAuthResponseDTO {

    @JsonProperty("token")
    private String token;

    @JsonProperty("role")
    private String role;               // always "DOCTOR"

    @JsonProperty("doctorId")
    private String doctorId;

    @JsonProperty("fullName")
    private String fullName;

    @JsonProperty("phone")
    private String phone;

    @JsonProperty("email")
    private String email;

    @JsonProperty("specialization")
    private String specialization;

    @JsonProperty("hospital")
    private String hospital;

    @JsonProperty("district")
    private String district;

    @JsonProperty("registrationNo")
    private String registrationNo;

    @JsonProperty("isAvailable")
    private Boolean isAvailable;

    @JsonProperty("message")
    private String message;
}
```

---

## dto/ConsultationResponseDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Full consultation response sent to React.
 * Includes embedded patient snapshot and visit risk data
 * so the doctor doesn't need to make separate API calls.
 */
@Data
@Builder
public class ConsultationResponseDTO {

    @JsonProperty("consultationId")
    private String consultationId;

    @JsonProperty("status")
    private String status;

    @JsonProperty("riskLevel")
    private String riskLevel;

    @JsonProperty("isHighRisk")
    private Boolean isHighRisk;

    @JsonProperty("priorityScore")
    private Integer priorityScore;

    // ─── Patient snapshot ─────────────────────────────────────────────────────
    @JsonProperty("patientId")
    private String patientId;

    @JsonProperty("patientName")
    private String patientName;

    @JsonProperty("patientAge")
    private Integer patientAge;

    @JsonProperty("patientPhone")
    private String patientPhone;

    @JsonProperty("village")
    private String village;

    @JsonProperty("district")
    private String district;

    @JsonProperty("bloodGroup")
    private String bloodGroup;

    // ─── Visit + AI risk data ─────────────────────────────────────────────────
    @JsonProperty("visitId")
    private String visitId;

    @JsonProperty("gestationalWeeks")
    private Integer gestationalWeeks;

    @JsonProperty("detectedRisks")
    private List<String> detectedRisks;

    @JsonProperty("explanation")
    private String explanation;

    @JsonProperty("confidence")
    private Double confidence;

    @JsonProperty("recommendation")
    private String recommendation;

    // ─── Worker info ──────────────────────────────────────────────────────────
    @JsonProperty("workerId")
    private String workerId;

    @JsonProperty("workerName")
    private String workerName;

    @JsonProperty("workerPhone")
    private String workerPhone;

    @JsonProperty("healthCenter")
    private String healthCenter;

    // ─── Doctor info ──────────────────────────────────────────────────────────
    @JsonProperty("doctorId")
    private String doctorId;

    @JsonProperty("doctorName")
    private String doctorName;

    // ─── Video call ───────────────────────────────────────────────────────────
    @JsonProperty("roomUrl")
    private String roomUrl;

    @JsonProperty("doctorToken")
    private String doctorToken;

    @JsonProperty("workerToken")
    private String workerToken;

    // ─── Doctor notes ─────────────────────────────────────────────────────────
    @JsonProperty("doctorNotes")
    private String doctorNotes;

    @JsonProperty("diagnosis")
    private String diagnosis;

    @JsonProperty("actionPlan")
    private String actionPlan;

    // ─── Timestamps ───────────────────────────────────────────────────────────
    @JsonProperty("acceptedAt")
    private LocalDateTime acceptedAt;

    @JsonProperty("callStartedAt")
    private LocalDateTime callStartedAt;

    @JsonProperty("completedAt")
    private LocalDateTime completedAt;

    @JsonProperty("createdAt")
    private LocalDateTime createdAt;
}
```

---

## dto/ConsultationNotesRequestDTO.java

```java
package com.anc.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Doctor submits notes when completing consultation:
 * {
 *   "doctorNotes": "Patient has severe pre-eclampsia with HELLP syndrome features...",
 *   "diagnosis":   "Severe Pre-eclampsia with superimposed anaemia",
 *   "actionPlan":  "1. Immediate referral to CEmOC. 2. IV MgSO4. 3. Blood transfusion."
 * }
 */
@Data
public class ConsultationNotesRequestDTO {

    @NotBlank(message = "Doctor notes are required")
    @JsonProperty("doctorNotes")
    private String doctorNotes;

    @JsonProperty("diagnosis")
    private String diagnosis;

    @NotBlank(message = "Action plan is required")
    @JsonProperty("actionPlan")
    private String actionPlan;
}
```

---

## service/VideoSessionService.java

```java
package com.anc.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Manages Daily.co video rooms for teleconsultation.
 *
 * HOW DAILY.CO WORKS:
 *   1. Create a room via Daily.co REST API → get room URL
 *   2. Generate meeting tokens for doctor + worker (with different permissions)
 *   3. React embeds Daily.co using their JS SDK (@daily-co/daily-js)
 *      or iframe with the room URL + token
 *
 * FREE TIER: daily.co free plan supports up to 200 participants/month.
 *
 * Get API key at: https://dashboard.daily.co/
 */
@Slf4j
@Service
public class VideoSessionService {

    @Value("${daily.api-key}")
    private String dailyApiKey;

    @Value("${daily.base-url:https://api.daily.co/v1}")
    private String dailyBaseUrl;

    @Value("${daily.domain}")
    private String dailyDomain;

    private final RestTemplate restTemplate;

    public VideoSessionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Create a Daily.co room for a consultation.
     * Room name = "consult-{consultationId}" (first 8 chars of UUID)
     *
     * @return room URL e.g. "https://anc-portal.daily.co/consult-abc12345"
     */
    public String createRoom(String consultationId) {
        String roomName = "consult-" + consultationId.substring(0, 8);
        String url      = dailyBaseUrl + "/rooms";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + dailyApiKey);

        Map<String, Object> properties = new HashMap<>();
        properties.put("exp", (System.currentTimeMillis() / 1000) + 7200); // 2 hour expiry
        properties.put("enable_chat", true);
        properties.put("enable_screenshare", false);
        properties.put("max_participants", 2);  // doctor + worker only

        Map<String, Object> body = new HashMap<>();
        body.put("name", roomName);
        body.put("privacy", "private");
        body.put("properties", properties);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            String roomUrl = (String) response.getBody().get("url");
            log.info("Daily.co room created: {}", roomUrl);
            return roomUrl;
        } catch (Exception e) {
            log.error("Failed to create Daily.co room: {}", e.getMessage());
            // Fallback: return a placeholder URL (for dev/testing without Daily.co key)
            return "https://" + dailyDomain + ".daily.co/" + roomName;
        }
    }

    /**
     * Generate a meeting token for a participant.
     *
     * @param roomName   the Daily.co room name
     * @param userName   display name in the call
     * @param isOwner    true for doctor (owner = can end call, mute others)
     * @return token string to pass to Daily.co JS SDK
     */
    public String generateToken(String roomName, String userName, boolean isOwner) {
        String url = dailyBaseUrl + "/meeting-tokens";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + dailyApiKey);

        Map<String, Object> properties = new HashMap<>();
        properties.put("room_name", roomName);
        properties.put("user_name", userName);
        properties.put("is_owner", isOwner);
        properties.put("exp", (System.currentTimeMillis() / 1000) + 7200);
        properties.put("enable_recording", false);

        Map<String, Object> body = new HashMap<>();
        body.put("properties", properties);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            return (String) response.getBody().get("token");
        } catch (Exception e) {
            log.error("Failed to generate Daily.co token: {}", e.getMessage());
            return "dev-token-" + userName.replaceAll("\\s", "-");
        }
    }
}
```

---

## service/DoctorAuthService.java

```java
package com.anc.service;

import com.anc.dto.DoctorAuthResponseDTO;
import com.anc.dto.DoctorLoginRequestDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class DoctorAuthService {

    private final DoctorRepository doctorRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public DoctorAuthResponseDTO signup(DoctorSignupRequestDTO request) {
        log.info("Doctor signup for phone: {}", request.getPhone());

        if (doctorRepository.existsByPhone(request.getPhone())) {
            throw new RuntimeException("Phone number already registered");
        }
        if (request.getEmail() != null && doctorRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        DoctorEntity doctor = DoctorEntity.builder()
                .fullName(request.getFullName())
                .phone(request.getPhone())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .specialization(
                    request.getSpecialization() != null
                        ? request.getSpecialization()
                        : "Obstetrics & Gynaecology"
                )
                .hospital(request.getHospital())
                .district(request.getDistrict())
                .registrationNo(request.getRegistrationNo())
                .isActive(true)
                .isAvailable(true)
                .build();

        doctor = doctorRepository.save(doctor);
        log.info("Doctor created — ID: {}", doctor.getId());

        // Pass role="DOCTOR" so JwtService embeds it in the token
        String token = jwtService.generateToken(doctor.getPhone(), doctor.getId(), "DOCTOR");
        return buildResponse(doctor, token, "Account created successfully");
    }

    public DoctorAuthResponseDTO login(DoctorLoginRequestDTO request) {
        log.info("Doctor login for phone: {}", request.getPhone());

        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getPhone(), request.getPassword())
        );

        DoctorEntity doctor = doctorRepository.findByPhone(request.getPhone())
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        String token = jwtService.generateToken(doctor.getPhone(), doctor.getId(), "DOCTOR");
        return buildResponse(doctor, token, "Login successful");
    }

    private DoctorAuthResponseDTO buildResponse(DoctorEntity doctor, String token, String message) {
        return DoctorAuthResponseDTO.builder()
                .token(token)
                .role("DOCTOR")
                .doctorId(doctor.getId())
                .fullName(doctor.getFullName())
                .phone(doctor.getPhone())
                .email(doctor.getEmail())
                .specialization(doctor.getSpecialization())
                .hospital(doctor.getHospital())
                .district(doctor.getDistrict())
                .registrationNo(doctor.getRegistrationNo())
                .isAvailable(doctor.getIsAvailable())
                .message(message)
                .build();
    }
}
```

---

## service/JwtService.java — UPDATE generateToken()

```java
// Replace existing generateToken() with this overloaded version
// that accepts a role parameter. Keep all other methods unchanged.

/**
 * Generate JWT for ANC Worker (role = "WORKER")
 */
public String generateToken(String phone, String userId) {
    return generateToken(phone, userId, "WORKER");
}

/**
 * Generate JWT for any user type with explicit role.
 * Role is stored in JWT claims and used by SecurityConfig
 * to enforce role-based endpoint access.
 */
public String generateToken(String phone, String userId, String role) {
    Map<String, Object> claims = new HashMap<>();
    claims.put("userId", userId);
    claims.put("role", role);   // "WORKER" or "DOCTOR"
    return buildToken(claims, phone);
}

/**
 * Extract role from JWT claims.
 * Used by SecurityConfig and controllers to enforce role checks.
 */
public String extractRole(String token) {
    return extractClaim(token, claims -> claims.get("role", String.class));
}

/**
 * Extract userId (workerId or doctorId depending on role).
 */
public String extractUserId(String token) {
    return extractClaim(token, claims -> claims.get("userId", String.class));
}
```

---

## security/CustomUserDetailsService.java — UPDATE to check both tables

```java
package com.anc.security;

import com.anc.repository.AncWorkerRepository;
import com.anc.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

/**
 * Updated to check BOTH anc_workers and doctors tables by phone number.
 *
 * Spring Security calls loadUserByUsername(phone) for every authenticated request.
 * We try the worker table first, then the doctor table.
 * If neither has this phone: throw UsernameNotFoundException → 401.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final AncWorkerRepository workerRepository;
    private final DoctorRepository    doctorRepository;

    @Override
    public UserDetails loadUserByUsername(String phone) throws UsernameNotFoundException {
        log.debug("Loading user by phone: {}", phone);

        // Check ANC workers first
        var worker = workerRepository.findByPhone(phone);
        if (worker.isPresent()) {
            log.debug("Found ANC worker for phone: {}", phone);
            return worker.get();
        }

        // Then check doctors
        var doctor = doctorRepository.findByPhone(phone);
        if (doctor.isPresent()) {
            log.debug("Found doctor for phone: {}", phone);
            return doctor.get();
        }

        log.warn("No user found for phone: {}", phone);
        throw new UsernameNotFoundException("No user registered with phone: " + phone);
    }
}
```

---

## security/SecurityConfig.java — UPDATE with doctor role rules

```java
// Replace the authorizeHttpRequests block in SecurityConfig.java with this:

.authorizeHttpRequests(auth -> auth
    // ── Public ──────────────────────────────────────────────
    .requestMatchers("/api/auth/signup").permitAll()
    .requestMatchers("/api/auth/login").permitAll()
    .requestMatchers("/api/doctor/auth/signup").permitAll()
    .requestMatchers("/api/doctor/auth/login").permitAll()

    // ── Doctor-only ──────────────────────────────────────────
    .requestMatchers("/api/doctor/auth/me").hasRole("DOCTOR")
    .requestMatchers("/api/consultations/queue").hasRole("DOCTOR")
    .requestMatchers("/api/consultations/my-history").hasRole("DOCTOR")
    .requestMatchers(HttpMethod.POST, "/api/consultations/*/accept").hasRole("DOCTOR")
    .requestMatchers(HttpMethod.POST, "/api/consultations/*/start-call").hasRole("DOCTOR")
    .requestMatchers(HttpMethod.POST, "/api/consultations/*/complete").hasRole("DOCTOR")

    // ── Both roles (worker sees patient consultations, doctor sees them too) ──
    .requestMatchers("/api/consultations/**").authenticated()

    // ── Everything else needs valid JWT ─────────────────────
    .anyRequest().authenticated()
)
```

---

## service/ConsultationService.java

```java
package com.anc.service;

import com.anc.dto.ConsultationNotesRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.*;
import com.anc.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Core consultation logic:
 *
 *  createFromVisit()  → called by AncVisitService when isHighRisk=true
 *  getPriorityQueue() → doctor's queue, CRITICAL first
 *  accept()           → doctor claims the case
 *  startCall()        → creates Daily.co room + tokens
 *  complete()         → saves doctor notes, marks COMPLETED
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ConsultationService {

    private final ConsultationRepository  consultationRepository;
    private final PatientRepository       patientRepository;
    private final AncWorkerRepository     workerRepository;
    private final DoctorRepository        doctorRepository;
    private final AncVisitRepository      visitRepository;
    private final VideoSessionService     videoSessionService;

    /**
     * Auto-called from AncVisitService after FastAPI returns isHighRisk=true.
     * Creates a PENDING consultation in the priority queue.
     */
    @Transactional
    public void createFromVisit(AncVisitEntity visit) {
        // Skip if a pending/accepted consultation already exists for this visit
        if (consultationRepository.existsByVisitIdAndStatusIn(
                visit.getId(), List.of("PENDING", "ACCEPTED", "IN_PROGRESS"))) {
            log.info("Consultation already exists for visit: {}", visit.getId());
            return;
        }

        int priorityScore = switch (visit.getRiskLevel()) {
            case "CRITICAL" -> 100;
            case "HIGH"     -> 70;
            case "MEDIUM"   -> 40;
            default         -> 10;
        };

        ConsultationEntity consultation = ConsultationEntity.builder()
                .visitId(visit.getId())
                .patientId(visit.getPatientId())
                .workerId(visit.getWorkerId())
                .riskLevel(visit.getRiskLevel())
                .isHighRisk(visit.getIsHighRisk())
                .priorityScore(priorityScore)
                .status("PENDING")
                .build();

        consultationRepository.save(consultation);
        log.info("Consultation created — visitId: {}, riskLevel: {}, priority: {}",
                visit.getId(), visit.getRiskLevel(), priorityScore);
    }

    /**
     * Returns priority-sorted queue for the authenticated doctor.
     * CRITICAL (100) → HIGH (70) → MEDIUM (40), oldest first within same tier.
     */
    public List<ConsultationResponseDTO> getPriorityQueue(String doctorId) {
        DoctorEntity doctor = doctorRepository.findById(doctorId)
                .orElseThrow(() -> new RuntimeException("Doctor not found"));

        List<ConsultationEntity> queue = consultationRepository.findPriorityQueue();
        return queue.stream().map(this::toResponseDTO).collect(Collectors.toList());
    }

    /**
     * Doctor accepts a pending consultation.
     * Sets status = ACCEPTED, assigns doctorId.
     */
    @Transactional
    public ConsultationResponseDTO accept(String consultationId, String doctorId) {
        ConsultationEntity c = getConsultation(consultationId);

        if (!"PENDING".equals(c.getStatus())) {
            throw new RuntimeException(
                "Cannot accept consultation with status: " + c.getStatus()
            );
        }

        c.setDoctorId(doctorId);
        c.setStatus("ACCEPTED");
        c.setAcceptedAt(LocalDateTime.now());
        consultationRepository.save(c);

        log.info("Doctor {} accepted consultation {}", doctorId, consultationId);
        return toResponseDTO(c);
    }

    /**
     * Doctor starts the video call.
     * Creates Daily.co room + generates tokens for doctor and worker.
     * Sets status = IN_PROGRESS.
     */
    @Transactional
    public ConsultationResponseDTO startCall(String consultationId, String doctorId) {
        ConsultationEntity c = getConsultation(consultationId);

        if (!doctorId.equals(c.getDoctorId())) {
            throw new RuntimeException("You are not the assigned doctor for this consultation");
        }
        if (!"ACCEPTED".equals(c.getStatus()) && !"IN_PROGRESS".equals(c.getStatus())) {
            throw new RuntimeException("Accept the consultation before starting the call");
        }

        // Create Daily.co room if not already created
        if (c.getRoomUrl() == null) {
            String roomUrl = videoSessionService.createRoom(consultationId);
            String roomName = "consult-" + consultationId.substring(0, 8);

            // Get names for Daily.co display
            String doctorName = doctorRepository.findById(doctorId)
                    .map(d -> "Dr. " + d.getFullName()).orElse("Doctor");
            String workerName = workerRepository.findById(c.getWorkerId())
                    .map(AncWorkerEntity::getFullName).orElse("ANC Worker");

            String doctorToken = videoSessionService.generateToken(roomName, doctorName, true);
            String workerToken = videoSessionService.generateToken(roomName, workerName, false);

            c.setRoomUrl(roomUrl);
            c.setDoctorToken(doctorToken);
            c.setWorkerToken(workerToken);
        }

        c.setStatus("IN_PROGRESS");
        c.setCallStartedAt(LocalDateTime.now());
        consultationRepository.save(c);

        log.info("Video call started for consultation {}", consultationId);
        return toResponseDTO(c);
    }

    /**
     * Doctor submits consultation notes and closes the case.
     * Sets status = COMPLETED.
     */
    @Transactional
    public ConsultationResponseDTO complete(
            String consultationId,
            String doctorId,
            ConsultationNotesRequestDTO notes) {

        ConsultationEntity c = getConsultation(consultationId);

        if (!doctorId.equals(c.getDoctorId())) {
            throw new RuntimeException("You are not the assigned doctor for this consultation");
        }

        c.setDoctorNotes(notes.getDoctorNotes());
        c.setDiagnosis(notes.getDiagnosis());
        c.setActionPlan(notes.getActionPlan());
        c.setStatus("COMPLETED");
        c.setCompletedAt(LocalDateTime.now());
        consultationRepository.save(c);

        log.info("Consultation {} completed by doctor {}", consultationId, doctorId);
        return toResponseDTO(c);
    }

    /** Doctor's completed consultation history */
    public List<ConsultationResponseDTO> getDoctorHistory(String doctorId) {
        return consultationRepository.findByDoctorIdOrderByCreatedAtDesc(doctorId)
                .stream().map(this::toResponseDTO).collect(Collectors.toList());
    }

    /** Worker views consultations for their patient */
    public List<ConsultationResponseDTO> getPatientConsultations(String patientId) {
        return consultationRepository.findByPatientIdOrderByCreatedAtDesc(patientId)
                .stream().map(this::toResponseDTO).collect(Collectors.toList());
    }

    public ConsultationResponseDTO getById(String consultationId) {
        return toResponseDTO(getConsultation(consultationId));
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    private ConsultationEntity getConsultation(String id) {
        return consultationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Consultation not found: " + id));
    }

    /**
     * Builds the full ConsultationResponseDTO by joining:
     *   consultation → patient → worker → doctor → visit
     */
    private ConsultationResponseDTO toResponseDTO(ConsultationEntity c) {
        ConsultationResponseDTO.ConsultationResponseDTOBuilder b =
                ConsultationResponseDTO.builder()
                        .consultationId(c.getId())
                        .status(c.getStatus())
                        .riskLevel(c.getRiskLevel())
                        .isHighRisk(c.getIsHighRisk())
                        .priorityScore(c.getPriorityScore())
                        .visitId(c.getVisitId())
                        .patientId(c.getPatientId())
                        .workerId(c.getWorkerId())
                        .doctorId(c.getDoctorId())
                        .roomUrl(c.getRoomUrl())
                        .doctorToken(c.getDoctorToken())
                        .workerToken(c.getWorkerToken())
                        .doctorNotes(c.getDoctorNotes())
                        .diagnosis(c.getDiagnosis())
                        .actionPlan(c.getActionPlan())
                        .acceptedAt(c.getAcceptedAt())
                        .callStartedAt(c.getCallStartedAt())
                        .completedAt(c.getCompletedAt())
                        .createdAt(c.getCreatedAt());

        // Enrich from patient
        patientRepository.findById(c.getPatientId()).ifPresent(p -> {
            b.patientName(p.getFullName())
             .patientAge(p.getAge())
             .patientPhone(p.getPhone())
             .village(p.getVillage())
             .district(p.getDistrict())
             .bloodGroup(p.getBloodGroup());
        });

        // Enrich from worker
        workerRepository.findById(c.getWorkerId()).ifPresent(w -> {
            b.workerName(w.getFullName())
             .workerPhone(w.getPhone())
             .healthCenter(w.getHealthCenter());
        });

        // Enrich from doctor
        if (c.getDoctorId() != null) {
            doctorRepository.findById(c.getDoctorId()).ifPresent(d ->
                b.doctorName(d.getFullName())
            );
        }

        // Enrich from visit (AI risk data)
        visitRepository.findById(c.getVisitId()).ifPresent(v -> {
            b.gestationalWeeks(
                v.getStructuredData() != null
                    ? extractGestationalWeeks(v.getStructuredData())
                    : null
            )
            .detectedRisks(v.getDetectedRisks())
            .explanation(v.getExplanation())
            .confidence(v.getConfidence())
            .recommendation(v.getRecommendation());
        });

        return b.build();
    }

    @SuppressWarnings("unchecked")
    private Integer extractGestationalWeeks(java.util.Map<String, Object> structuredData) {
        try {
            var patientInfo = (java.util.Map<String, Object>) structuredData.get("patient_info");
            if (patientInfo != null) {
                Object gw = patientInfo.get("gestationalWeeks");
                if (gw instanceof Number) return ((Number) gw).intValue();
            }
        } catch (Exception ignored) {}
        return null;
    }
}
```

---

## service/AncVisitService.java — UPDATE registerVisit() to trigger consultation

```java
// In AncVisitService.registerVisit(), after the final visitRepository.save():
// Add these lines BEFORE the return statement:

@Autowired
private ConsultationService consultationService;

// ── Auto-create consultation if high risk ──────────────────────────────────────
// This is the trigger point: if FastAPI says isHighRisk=true,
// a PENDING consultation is created in the doctor's queue automatically.
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

---

## controller/DoctorAuthController.java

```java
package com.anc.controller;

import com.anc.dto.DoctorAuthResponseDTO;
import com.anc.dto.DoctorLoginRequestDTO;
import com.anc.dto.DoctorSignupRequestDTO;
import com.anc.entity.DoctorEntity;
import com.anc.service.DoctorAuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/doctor/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DoctorAuthController {

    private final DoctorAuthService doctorAuthService;

    /**
     * POST /api/doctor/auth/signup
     *
     * Body: { fullName, phone, email, password, specialization, hospital, district, registrationNo }
     * Response: { token, role="DOCTOR", doctorId, fullName, specialization, hospital, ... }
     */
    @PostMapping("/signup")
    public ResponseEntity<DoctorAuthResponseDTO> signup(
            @Valid @RequestBody DoctorSignupRequestDTO request) {

        log.info("Doctor signup for phone: {}", request.getPhone());
        return ResponseEntity.status(HttpStatus.CREATED).body(doctorAuthService.signup(request));
    }

    /**
     * POST /api/doctor/auth/login
     *
     * Body: { phone, password }
     * Response: { token, role="DOCTOR", doctorId, fullName, ... }
     */
    @PostMapping("/login")
    public ResponseEntity<DoctorAuthResponseDTO> login(
            @Valid @RequestBody DoctorLoginRequestDTO request) {

        log.info("Doctor login for phone: {}", request.getPhone());
        return ResponseEntity.ok(doctorAuthService.login(request));
    }

    /**
     * GET /api/doctor/auth/me
     * Header: Authorization: Bearer <token>
     */
    @GetMapping("/me")
    public ResponseEntity<DoctorAuthResponseDTO> getMe(
            @AuthenticationPrincipal DoctorEntity doctor) {

        DoctorAuthResponseDTO response = DoctorAuthResponseDTO.builder()
                .doctorId(doctor.getId())
                .role("DOCTOR")
                .fullName(doctor.getFullName())
                .phone(doctor.getPhone())
                .email(doctor.getEmail())
                .specialization(doctor.getSpecialization())
                .hospital(doctor.getHospital())
                .district(doctor.getDistrict())
                .registrationNo(doctor.getRegistrationNo())
                .isAvailable(doctor.getIsAvailable())
                .message("Profile fetched")
                .build();

        return ResponseEntity.ok(response);
    }
}
```

---

## controller/ConsultationController.java

```java
package com.anc.controller;

import com.anc.dto.ConsultationNotesRequestDTO;
import com.anc.dto.ConsultationResponseDTO;
import com.anc.entity.DoctorEntity;
import com.anc.service.ConsultationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/consultations")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ConsultationController {

    private final ConsultationService consultationService;

    /**
     * GET /api/consultations/queue
     * ROLE: DOCTOR only
     *
     * Returns priority-sorted consultation queue.
     * CRITICAL cases (score=100) shown first.
     * Doctor uses this as their main work list.
     */
    @GetMapping("/queue")
    public ResponseEntity<List<ConsultationResponseDTO>> getPriorityQueue(
            @AuthenticationPrincipal DoctorEntity doctor) {

        log.info("Doctor {} requesting priority queue", doctor.getId());
        return ResponseEntity.ok(consultationService.getPriorityQueue(doctor.getId()));
    }

    /**
     * GET /api/consultations/{consultationId}
     * ROLE: DOCTOR or WORKER
     *
     * Full consultation detail with patient info, visit risk data.
     */
    @GetMapping("/{consultationId}")
    public ResponseEntity<ConsultationResponseDTO> getConsultation(
            @PathVariable String consultationId) {

        return ResponseEntity.ok(consultationService.getById(consultationId));
    }

    /**
     * POST /api/consultations/{consultationId}/accept
     * ROLE: DOCTOR only
     *
     * Doctor claims a PENDING consultation.
     * Sets status = ACCEPTED, assigns doctorId.
     */
    @PostMapping("/{consultationId}/accept")
    public ResponseEntity<ConsultationResponseDTO> accept(
            @PathVariable String consultationId,
            @AuthenticationPrincipal DoctorEntity doctor) {

        log.info("Doctor {} accepting consultation {}", doctor.getId(), consultationId);
        return ResponseEntity.ok(consultationService.accept(consultationId, doctor.getId()));
    }

    /**
     * POST /api/consultations/{consultationId}/start-call
     * ROLE: DOCTOR only
     *
     * Creates Daily.co room, generates doctor + worker tokens.
     * Sets status = IN_PROGRESS.
     * Returns roomUrl + doctorToken for the React video component.
     */
    @PostMapping("/{consultationId}/start-call")
    public ResponseEntity<ConsultationResponseDTO> startCall(
            @PathVariable String consultationId,
            @AuthenticationPrincipal DoctorEntity doctor) {

        log.info("Doctor {} starting call for consultation {}", doctor.getId(), consultationId);
        return ResponseEntity.ok(consultationService.startCall(consultationId, doctor.getId()));
    }

    /**
     * POST /api/consultations/{consultationId}/complete
     * ROLE: DOCTOR only
     *
     * Body: { doctorNotes, diagnosis, actionPlan }
     * Sets status = COMPLETED.
     */
    @PostMapping("/{consultationId}/complete")
    public ResponseEntity<ConsultationResponseDTO> complete(
            @PathVariable String consultationId,
            @AuthenticationPrincipal DoctorEntity doctor,
            @Valid @RequestBody ConsultationNotesRequestDTO notes) {

        log.info("Doctor {} completing consultation {}", doctor.getId(), consultationId);
        return ResponseEntity.ok(consultationService.complete(consultationId, doctor.getId(), notes));
    }

    /**
     * GET /api/consultations/my-history
     * ROLE: DOCTOR only
     *
     * Returns doctor's past completed consultations.
     */
    @GetMapping("/my-history")
    public ResponseEntity<List<ConsultationResponseDTO>> getMyHistory(
            @AuthenticationPrincipal DoctorEntity doctor) {

        return ResponseEntity.ok(consultationService.getDoctorHistory(doctor.getId()));
    }

    /**
     * GET /api/consultations/patient/{patientId}
     * ROLE: WORKER (to see their patient's consultation status + doctor notes)
     *
     * Worker uses this on the PatientDetailPage to see if/when a doctor
     * has reviewed their high-risk patient.
     */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<ConsultationResponseDTO>> getPatientConsultations(
            @PathVariable String patientId) {

        return ResponseEntity.ok(consultationService.getPatientConsultations(patientId));
    }
}
```

---

# React Doctor Portal — Frontend

---

## New Files (add to existing React project)

```
src/
├── api/
│   ├── doctorApi.js              ← signup, login, getMe
│   └── consultationApi.js        ← queue, accept, startCall, complete
│
├── context/
│   └── DoctorAuthContext.jsx     ← doctor auth state (mirrors AuthContext)
│
├── hooks/
│   └── useDoctorAuth.js
│
├── routes/
│   └── DoctorProtectedRoute.jsx  ← redirect if not DOCTOR role
│
├── pages/doctor/
│   ├── DoctorLoginPage.jsx
│   ├── DoctorSignupPage.jsx
│   ├── DoctorQueuePage.jsx       ← priority queue dashboard
│   ├── ConsultationDetailPage.jsx← patient info + risk data
│   ├── VideoCallPage.jsx         ← Daily.co video embed
│   └── DoctorHistoryPage.jsx     ← past consultations
│
└── components/doctor/
    ├── DoctorLayout.jsx           ← sidebar layout for doctor portal
    ├── ConsultationCard.jsx       ← queue item card
    ├── PriorityBadge.jsx          ← CRITICAL/HIGH/MEDIUM with urgency styling
    └── VideoRoom.jsx              ← Daily.co iframe component
```

---

## src/api/doctorApi.js

```js
import axiosInstance from './axiosInstance';

/**
 * POST /api/doctor/auth/signup
 * data: { fullName, phone, email, password, specialization, hospital, district, registrationNo }
 */
export const doctorSignup = async (data) => {
  const res = await axiosInstance.post('/api/doctor/auth/signup', data);
  return res.data; // DoctorAuthResponseDTO
};

/**
 * POST /api/doctor/auth/login
 * data: { phone, password }
 */
export const doctorLogin = async (data) => {
  const res = await axiosInstance.post('/api/doctor/auth/login', data);
  return res.data; // DoctorAuthResponseDTO { token, role="DOCTOR", doctorId, ... }
};

export const getDoctorMe = async () => {
  const res = await axiosInstance.get('/api/doctor/auth/me');
  return res.data;
};
```

---

## src/api/consultationApi.js

```js
import axiosInstance from './axiosInstance';

/** GET /api/consultations/queue — priority sorted, CRITICAL first */
export const getPriorityQueue = async () => {
  const res = await axiosInstance.get('/api/consultations/queue');
  return res.data; // ConsultationResponseDTO[]
};

/** GET /api/consultations/{id} */
export const getConsultation = async (id) => {
  const res = await axiosInstance.get(`/api/consultations/${id}`);
  return res.data;
};

/** POST /api/consultations/{id}/accept */
export const acceptConsultation = async (id) => {
  const res = await axiosInstance.post(`/api/consultations/${id}/accept`);
  return res.data;
};

/**
 * POST /api/consultations/{id}/start-call
 * Returns { roomUrl, doctorToken, workerToken, status: "IN_PROGRESS" }
 */
export const startCall = async (id) => {
  const res = await axiosInstance.post(`/api/consultations/${id}/start-call`);
  return res.data;
};

/**
 * POST /api/consultations/{id}/complete
 * body: { doctorNotes, diagnosis, actionPlan }
 */
export const completeConsultation = async (id, notes) => {
  const res = await axiosInstance.post(`/api/consultations/${id}/complete`, notes);
  return res.data;
};

/** GET /api/consultations/my-history */
export const getDoctorHistory = async () => {
  const res = await axiosInstance.get('/api/consultations/my-history');
  return res.data;
};

/** GET /api/consultations/patient/{patientId} — used by worker */
export const getPatientConsultations = async (patientId) => {
  const res = await axiosInstance.get(`/api/consultations/patient/${patientId}`);
  return res.data;
};
```

---

## src/context/DoctorAuthContext.jsx

```jsx
import { createContext, useState, useEffect, useCallback } from 'react';
import { doctorLogin, doctorSignup } from '../api/doctorApi';

/**
 * Doctor authentication context.
 * Mirrors AuthContext but stores: doctor, role="DOCTOR", token.
 *
 * localStorage keys:
 *   'anc_token'   → shared JWT key (axiosInstance reads this)
 *   'anc_doctor'  → doctor profile JSON
 *   'anc_role'    → "DOCTOR" (used by routes to differentiate)
 */
export const DoctorAuthContext = createContext(null);

export function DoctorAuthProvider({ children }) {
  const [doctor, setDoctor]     = useState(null);
  const [token, setToken]       = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken  = localStorage.getItem('anc_token');
    const storedDoctor = localStorage.getItem('anc_doctor');
    const storedRole   = localStorage.getItem('anc_role');

    if (storedToken && storedDoctor && storedRole === 'DOCTOR') {
      try {
        setToken(storedToken);
        setDoctor(JSON.parse(storedDoctor));
      } catch {
        clearStorage();
      }
    }
    setIsLoading(false);
  }, []);

  const persistDoctor = (authResponse) => {
    const { token, ...doctorInfo } = authResponse;
    localStorage.setItem('anc_token',  token);
    localStorage.setItem('anc_doctor', JSON.stringify(doctorInfo));
    localStorage.setItem('anc_role',   'DOCTOR');
    setToken(token);
    setDoctor(doctorInfo);
  };

  const login = useCallback(async (phone, password) => {
    const res = await doctorLogin({ phone, password });
    persistDoctor(res);
    return res;
  }, []);

  const signup = useCallback(async (formData) => {
    const res = await doctorSignup(formData);
    persistDoctor(res);
    return res;
  }, []);

  const logout = useCallback(() => {
    clearStorage();
    setToken(null);
    setDoctor(null);
    window.location.href = '/doctor/login';
  }, []);

  const value = {
    doctor,
    token,
    isLoading,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
  };

  return (
    <DoctorAuthContext.Provider value={value}>
      {children}
    </DoctorAuthContext.Provider>
  );
}

function clearStorage() {
  localStorage.removeItem('anc_token');
  localStorage.removeItem('anc_doctor');
  localStorage.removeItem('anc_role');
}
```

---

## src/hooks/useDoctorAuth.js

```js
import { useContext } from 'react';
import { DoctorAuthContext } from '../context/DoctorAuthContext';

export function useDoctorAuth() {
  const ctx = useContext(DoctorAuthContext);
  if (!ctx) throw new Error('useDoctorAuth must be inside <DoctorAuthProvider>');
  return ctx;
}
```

---

## src/routes/DoctorProtectedRoute.jsx

```jsx
import { Navigate, Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../hooks/useDoctorAuth';
import Spinner from '../components/ui/Spinner';

export default function DoctorProtectedRoute() {
  const { isAuthenticated, isLoading } = useDoctorAuth();

  if (isLoading) return (
    <div className="flex items-center justify-center min-h-screen">
      <Spinner size="lg" />
    </div>
  );

  return isAuthenticated
    ? <Outlet />
    : <Navigate to="/doctor/login" replace />;
}
```

---

## src/components/doctor/PriorityBadge.jsx

```jsx
/**
 * Priority badge — larger and more prominent than the regular Badge.
 * Used in the consultation queue to signal urgency.
 */
export default function PriorityBadge({ riskLevel }) {
  const config = {
    CRITICAL: {
      bg: 'bg-red-600', text: 'text-white',
      label: '🚨 CRITICAL', pulse: true,
    },
    HIGH: {
      bg: 'bg-orange-500', text: 'text-white',
      label: '⚠ HIGH', pulse: false,
    },
    MEDIUM: {
      bg: 'bg-yellow-400', text: 'text-gray-900',
      label: '⚡ MEDIUM', pulse: false,
    },
  };

  const c = config[riskLevel] || { bg: 'bg-gray-300', text: 'text-gray-700', label: riskLevel };

  return (
    <span className={`
      inline-flex items-center px-3 py-1 rounded-full text-sm font-bold
      ${c.bg} ${c.text}
      ${c.pulse ? 'animate-pulse' : ''}
    `}>
      {c.label}
    </span>
  );
}
```

---

## src/components/doctor/ConsultationCard.jsx

```jsx
import { useNavigate } from 'react-router-dom';
import PriorityBadge from './PriorityBadge';
import Button from '../ui/Button';

/**
 * Card shown in the doctor's priority queue.
 * Displays patient name, risk level, detected risks, age/weeks.
 * "Accept" button claims the consultation.
 *
 * Props: ConsultationResponseDTO fields + onAccept callback
 */
export default function ConsultationCard({ consultation, onAccept, accepting }) {
  const navigate = useNavigate();
  const {
    consultationId, riskLevel, status, patientName, patientAge,
    gestationalWeeks, detectedRisks, createdAt, healthCenter,
    village, district, workerName,
  } = consultation;

  const waitMinutes = Math.floor(
    (Date.now() - new Date(createdAt).getTime()) / 60000
  );

  return (
    <div className={`
      bg-white border-2 rounded-xl p-5 transition-all
      ${riskLevel === 'CRITICAL' ? 'border-red-400 shadow-red-100 shadow-md'
      : riskLevel === 'HIGH'     ? 'border-orange-300 shadow-orange-50 shadow-sm'
      :                            'border-yellow-200'}
    `}>
      {/* Top row */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <PriorityBadge riskLevel={riskLevel} />
            <span className="text-xs text-gray-400">
              Waiting {waitMinutes}m
            </span>
          </div>
          <h3 className="text-base font-bold text-gray-900">
            {patientName || 'Patient'}
          </h3>
          <p className="text-sm text-gray-500">
            {patientAge ? `Age ${patientAge}` : ''}
            {gestationalWeeks ? ` • ${gestationalWeeks} weeks` : ''}
            {village ? ` • ${village}, ${district}` : ''}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            ANC Worker: {workerName} — {healthCenter}
          </p>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium
          ${status === 'PENDING'   ? 'bg-gray-100 text-gray-600'
          : status === 'ACCEPTED'  ? 'bg-blue-100 text-blue-700'
          : status === 'IN_PROGRESS' ? 'bg-green-100 text-green-700'
          : 'bg-gray-100 text-gray-500'}`}>
          {status}
        </span>
      </div>

      {/* Detected risks */}
      {detectedRisks?.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-gray-400 mb-1">Detected Risk Factors:</p>
          <div className="flex flex-wrap gap-1">
            {detectedRisks.slice(0, 4).map((r, i) => (
              <span key={i} className="text-xs bg-red-50 text-red-700 border border-red-100 px-2 py-0.5 rounded-full">
                {r}
              </span>
            ))}
            {detectedRisks.length > 4 && (
              <span className="text-xs text-gray-400">+{detectedRisks.length - 4} more</span>
            )}
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2 pt-2 border-t border-gray-100">
        {status === 'PENDING' && (
          <Button
            variant="primary"
            loading={accepting}
            onClick={() => onAccept(consultationId)}
            className="flex-1"
          >
            ✅ Accept Case
          </Button>
        )}
        {(status === 'ACCEPTED' || status === 'IN_PROGRESS') && (
          <Button
            variant="primary"
            onClick={() => navigate(`/doctor/consultations/${consultationId}`)}
            className="flex-1"
          >
            {status === 'IN_PROGRESS' ? '📹 Rejoin Call' : '📋 Open Case'}
          </Button>
        )}
        <Button
          variant="ghost"
          onClick={() => navigate(`/doctor/consultations/${consultationId}`)}
        >
          View
        </Button>
      </div>
    </div>
  );
}
```

---

## src/components/doctor/VideoRoom.jsx

```jsx
import { useEffect, useRef } from 'react';

/**
 * Embeds a Daily.co video call using their iframe API.
 *
 * HOW IT WORKS:
 *   1. Loads the @daily-co/daily-js script dynamically
 *   2. Creates a DailyIframe inside the container div
 *   3. Joins the room using roomUrl + token
 *
 * The doctor passes doctorToken (owner=true — can mute, end call).
 * The worker passes workerToken (participant).
 *
 * Install: npm install @daily-co/daily-js
 *
 * Props:
 *   roomUrl   string  e.g. "https://anc-portal.daily.co/consult-abc12345"
 *   token     string  Daily.co meeting token for this user
 *   onLeave   function  called when user leaves the call
 */
export default function VideoRoom({ roomUrl, token, onLeave }) {
  const containerRef = useRef(null);
  const callRef      = useRef(null);

  useEffect(() => {
    if (!roomUrl || !containerRef.current) return;

    // Dynamically load Daily.co
    const loadDaily = async () => {
      const DailyIframe = (await import('@daily-co/daily-js')).default;

      // Destroy previous call if any
      if (callRef.current) {
        await callRef.current.destroy();
      }

      callRef.current = DailyIframe.createFrame(containerRef.current, {
        iframeStyle: {
          width:  '100%',
          height: '100%',
          border: 'none',
          borderRadius: '12px',
        },
        showLeaveButton: true,
        showFullscreenButton: true,
      });

      callRef.current.on('left-meeting', () => {
        if (onLeave) onLeave();
      });

      await callRef.current.join({ url: roomUrl, token });
    };

    loadDaily();

    return () => {
      if (callRef.current) {
        callRef.current.destroy();
        callRef.current = null;
      }
    };
  }, [roomUrl, token]);

  return (
    <div
      ref={containerRef}
      className="w-full bg-gray-900 rounded-xl overflow-hidden"
      style={{ height: '520px' }}
    />
  );
}
```

---

## src/components/doctor/DoctorLayout.jsx

```jsx
import { NavLink } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';

const navItems = [
  { to: '/doctor/queue',   label: 'Priority Queue', icon: '📋' },
  { to: '/doctor/history', label: 'My History',     icon: '📂' },
];

export default function DoctorLayout() {
  const { doctor, logout } = useDoctorAuth();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="px-6 py-5 border-b border-gray-100 bg-blue-700">
          <h1 className="text-lg font-bold text-white">Doctor Portal</h1>
          <p className="text-xs text-blue-200 mt-0.5">ANC Teleconsultation</p>
        </div>

        {doctor && (
          <div className="px-4 py-3 bg-blue-50 border-b border-blue-100">
            <p className="text-sm font-semibold text-blue-900">Dr. {doctor.fullName}</p>
            <p className="text-xs text-blue-600">{doctor.specialization}</p>
            <p className="text-xs text-blue-500">{doctor.hospital}</p>
          </div>
        )}

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'}`
              }
            >
              <span>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-gray-100">
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
          >
            🚪 Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorLoginPage.jsx

```jsx
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import InputField from '../../components/ui/InputField';
import Button from '../../components/ui/Button';
import ErrorAlert from '../../components/ui/ErrorAlert';

export default function DoctorLoginPage() {
  const { login }  = useDoctorAuth();
  const navigate   = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading]   = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      await login(data.phone, data.password);
      navigate('/doctor/queue');
    } catch (err) {
      setApiError(err.response?.data?.message || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 to-blue-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">👨‍⚕️</div>
          <h1 className="text-2xl font-bold text-gray-900">Doctor Portal</h1>
          <p className="text-gray-500 text-sm mt-1">ANC Teleconsultation System</p>
        </div>

        <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <InputField
            label="Phone Number"
            type="tel"
            placeholder="9988776655"
            error={errors.phone?.message}
            {...register('phone', {
              required: 'Phone is required',
              pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid phone number' },
            })}
          />
          <InputField
            label="Password"
            type="password"
            placeholder="••••••••"
            error={errors.password?.message}
            {...register('password', { required: 'Password is required' })}
          />
          <Button type="submit" loading={loading} className="w-full mt-2">
            Login as Doctor
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          New doctor?{' '}
          <Link to="/doctor/signup" className="text-blue-600 font-medium hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorSignupPage.jsx

```jsx
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import InputField from '../../components/ui/InputField';
import Button from '../../components/ui/Button';
import ErrorAlert from '../../components/ui/ErrorAlert';

export default function DoctorSignupPage() {
  const { signup } = useDoctorAuth();
  const navigate   = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading]   = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      await signup(data);
      navigate('/doctor/queue');
    } catch (err) {
      setApiError(err.response?.data?.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 to-blue-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-8">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">👨‍⚕️</div>
          <h1 className="text-2xl font-bold text-gray-900">Doctor Registration</h1>
          <p className="text-gray-500 text-sm">Join the ANC Teleconsultation Network</p>
        </div>

        <ErrorAlert message={apiError} onDismiss={() => setApiError(null)} />

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="grid grid-cols-2 gap-x-4">
            <div className="col-span-2">
              <InputField
                label="Full Name *"
                placeholder="Dr. Priya Sharma"
                error={errors.fullName?.message}
                {...register('fullName', { required: 'Full name is required' })}
              />
            </div>
            <InputField
              label="Phone *"
              type="tel"
              placeholder="9988776655"
              error={errors.phone?.message}
              {...register('phone', {
                required: 'Phone is required',
                pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid number' },
              })}
            />
            <InputField
              label="Email"
              type="email"
              placeholder="priya@hospital.in"
              {...register('email')}
            />
            <InputField
              label="Password *"
              type="password"
              placeholder="Min. 8 characters"
              error={errors.password?.message}
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Min 8 characters' },
              })}
            />
            <InputField
              label="Registration No."
              placeholder="KA-12345"
              {...register('registrationNo')}
            />
          </div>

          <InputField
            label="Specialization"
            placeholder="Obstetrics & Gynaecology"
            {...register('specialization')}
          />
          <InputField
            label="Hospital *"
            placeholder="District Hospital Bangalore Rural"
            error={errors.hospital?.message}
            {...register('hospital', { required: 'Hospital is required' })}
          />
          <InputField
            label="District *"
            placeholder="Bangalore Rural"
            error={errors.district?.message}
            {...register('district', { required: 'District is required' })}
          />

          <Button type="submit" loading={loading} className="w-full mt-2">
            Create Doctor Account
          </Button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Already registered?{' '}
          <Link to="/doctor/login" className="text-blue-600 font-medium hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorQueuePage.jsx

```jsx
import { useEffect, useState, useCallback } from 'react';
import { getPriorityQueue, acceptConsultation } from '../../api/consultationApi';
import { useDoctorAuth } from '../../hooks/useDoctorAuth';
import ConsultationCard from '../../components/doctor/ConsultationCard';
import Spinner from '../../components/ui/Spinner';
import ErrorAlert from '../../components/ui/ErrorAlert';

/**
 * Doctor's main dashboard — the priority queue.
 *
 * Shows all PENDING and ACCEPTED consultations sorted by:
 *   CRITICAL (score=100) → HIGH (70) → MEDIUM (40)
 *   Then oldest first within same tier.
 *
 * Auto-refreshes every 30 seconds so doctor sees new CRITICAL cases immediately.
 */
export default function DoctorQueuePage() {
  const { doctor }  = useDoctorAuth();
  const [queue, setQueue]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [accepting, setAccepting] = useState(null);

  const fetchQueue = useCallback(async () => {
    try {
      const data = await getPriorityQueue();
      setQueue(data);
      setError(null);
    } catch (err) {
      setError('Failed to load consultation queue');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => { fetchQueue(); }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchQueue, 30000);
    return () => clearInterval(interval);
  }, [fetchQueue]);

  const handleAccept = async (consultationId) => {
    setAccepting(consultationId);
    try {
      await acceptConsultation(consultationId);
      await fetchQueue(); // Refresh to show ACCEPTED status
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to accept consultation');
    } finally {
      setAccepting(null);
    }
  };

  const critical = queue.filter(c => c.riskLevel === 'CRITICAL');
  const high     = queue.filter(c => c.riskLevel === 'HIGH');
  const medium   = queue.filter(c => c.riskLevel === 'MEDIUM');

  if (loading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Patient Queue</h2>
          <p className="text-sm text-gray-500">
            Dr. {doctor?.fullName} • {queue.length} case{queue.length !== 1 ? 's' : ''} pending
            <span className="text-xs text-gray-400 ml-2">(auto-refreshes every 30s)</span>
          </p>
        </div>
        <button
          onClick={fetchQueue}
          className="text-sm text-blue-600 hover:underline"
        >
          ↻ Refresh
        </button>
      </div>

      <ErrorAlert message={error} onDismiss={() => setError(null)} />

      {queue.length === 0 && !loading && (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-3">✅</div>
          <p className="font-medium text-gray-600">No pending consultations</p>
          <p className="text-sm">All high-risk cases have been attended to.</p>
        </div>
      )}

      {/* CRITICAL section */}
      {critical.length > 0 && (
        <Section title="🚨 CRITICAL — Immediate Action Required" color="red" count={critical.length}>
          {critical.map(c => (
            <ConsultationCard
              key={c.consultationId}
              consultation={c}
              onAccept={handleAccept}
              accepting={accepting === c.consultationId}
            />
          ))}
        </Section>
      )}

      {/* HIGH section */}
      {high.length > 0 && (
        <Section title="⚠ HIGH Risk" color="orange" count={high.length}>
          {high.map(c => (
            <ConsultationCard
              key={c.consultationId}
              consultation={c}
              onAccept={handleAccept}
              accepting={accepting === c.consultationId}
            />
          ))}
        </Section>
      )}

      {/* MEDIUM section */}
      {medium.length > 0 && (
        <Section title="⚡ MEDIUM Risk" color="yellow" count={medium.length}>
          {medium.map(c => (
            <ConsultationCard
              key={c.consultationId}
              consultation={c}
              onAccept={handleAccept}
              accepting={accepting === c.consultationId}
            />
          ))}
        </Section>
      )}
    </div>
  );
}

function Section({ title, color, count, children }) {
  const borders = { red: 'border-red-200', orange: 'border-orange-200', yellow: 'border-yellow-200' };
  const headers = { red: 'text-red-700', orange: 'text-orange-700', yellow: 'text-yellow-700' };

  return (
    <div className={`mb-8 border-l-4 ${borders[color]} pl-4`}>
      <h3 className={`font-bold text-sm mb-3 ${headers[color]}`}>
        {title} ({count})
      </h3>
      <div className="space-y-4">{children}</div>
    </div>
  );
}
```

---

## src/pages/doctor/ConsultationDetailPage.jsx

```jsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  getConsultation, startCall, completeConsultation
} from '../../api/consultationApi';
import VideoRoom from '../../components/doctor/VideoRoom';
import PriorityBadge from '../../components/doctor/PriorityBadge';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import ErrorAlert from '../../components/ui/ErrorAlert';

/**
 * Full consultation page for the doctor.
 *
 * Shows:
 *   - Patient demographics (name, age, village, blood group)
 *   - AI risk assessment (riskLevel, detectedRisks, explanation, confidence)
 *   - "Start Video Call" → embeds Daily.co video room
 *   - Notes form → submit to complete consultation
 *   - ANC worker contact info
 */
export default function ConsultationDetailPage() {
  const { consultationId } = useParams();
  const navigate = useNavigate();

  const [consultation, setConsultation] = useState(null);
  const [loading, setLoading]     = useState(true);
  const [callLoading, setCallLoading] = useState(false);
  const [submitting, setSubmitting]   = useState(false);
  const [error, setError]         = useState(null);
  const [inCall, setInCall]       = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm();

  useEffect(() => {
    fetchConsultation();
  }, [consultationId]);

  const fetchConsultation = async () => {
    try {
      const data = await getConsultation(consultationId);
      setConsultation(data);
      if (data.status === 'IN_PROGRESS' && data.roomUrl) setInCall(true);
    } catch (err) {
      setError('Failed to load consultation');
    } finally {
      setLoading(false);
    }
  };

  const handleStartCall = async () => {
    setCallLoading(true);
    setError(null);
    try {
      const updated = await startCall(consultationId);
      setConsultation(updated);
      setInCall(true);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to start call');
    } finally {
      setCallLoading(false);
    }
  };

  const handleComplete = async (notes) => {
    setSubmitting(true);
    setError(null);
    try {
      await completeConsultation(consultationId, notes);
      navigate('/doctor/queue');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to complete consultation');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  if (!consultation) return <ErrorAlert message="Consultation not found" />;

  const {
    riskLevel, status, patientName, patientAge, patientPhone,
    gestationalWeeks, bloodGroup, village, district,
    detectedRisks, explanation, confidence, recommendation,
    workerName, workerPhone, healthCenter,
    roomUrl, doctorToken, doctorNotes, diagnosis, actionPlan
  } = consultation;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back + header */}
      <button
        onClick={() => navigate('/doctor/queue')}
        className="text-sm text-blue-600 hover:underline mb-4 flex items-center gap-1"
      >
        ← Back to Queue
      </button>

      <div className="flex items-center gap-3 mb-6">
        <PriorityBadge riskLevel={riskLevel} />
        <h2 className="text-xl font-bold text-gray-900">
          {patientName || 'Patient'} — Consultation
        </h2>
        <span className={`ml-auto text-xs px-3 py-1 rounded-full font-medium
          ${status === 'IN_PROGRESS' ? 'bg-green-100 text-green-700 animate-pulse'
          : status === 'COMPLETED'   ? 'bg-gray-100 text-gray-500'
          : 'bg-blue-100 text-blue-700'}`}>
          {status}
        </span>
      </div>

      <ErrorAlert message={error} onDismiss={() => setError(null)} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT COLUMN — Patient + Risk Data */}
        <div className="space-y-4">

          {/* Patient info */}
          <Card title="👤 Patient Details">
            <InfoRow label="Name"            value={patientName} />
            <InfoRow label="Age"             value={patientAge ? `${patientAge} years` : '—'} />
            <InfoRow label="Gestational Age" value={gestationalWeeks ? `${gestationalWeeks} weeks` : '—'} />
            <InfoRow label="Blood Group"     value={bloodGroup} />
            <InfoRow label="Phone"           value={patientPhone} />
            <InfoRow label="Location"        value={[village, district].filter(Boolean).join(', ')} />
          </Card>

          {/* AI Risk Assessment */}
          <Card title="🤖 AI Risk Assessment">
            <div className="flex items-center gap-2 mb-3">
              <PriorityBadge riskLevel={riskLevel} />
              {confidence != null && (
                <span className="text-xs text-gray-500">
                  Confidence: {Math.round(confidence * 100)}%
                </span>
              )}
            </div>

            {detectedRisks?.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-500 mb-1">Detected Risks:</p>
                <ul className="space-y-1">
                  {detectedRisks.map((r, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {explanation && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <p className="text-xs font-medium text-gray-500 mb-1">Explanation:</p>
                <p className="text-sm text-gray-700 leading-relaxed">{explanation}</p>
              </div>
            )}

            {recommendation && (
              <div className="mt-3 p-3 bg-red-50 border border-red-100 rounded-lg">
                <p className="text-xs font-medium text-red-600 mb-1">AI Recommendation:</p>
                <p className="text-sm text-red-800 font-medium">{recommendation}</p>
              </div>
            )}
          </Card>

          {/* ANC Worker info */}
          <Card title="👷 ANC Worker">
            <InfoRow label="Worker"        value={workerName} />
            <InfoRow label="Phone"         value={workerPhone} />
            <InfoRow label="Health Center" value={healthCenter} />
          </Card>
        </div>

        {/* RIGHT COLUMN — Video + Notes */}
        <div className="space-y-4">

          {/* Video call section */}
          <Card title="📹 Video Teleconsultation">
            {status === 'COMPLETED' ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-2xl mb-2">✅</p>
                <p className="font-medium">Consultation Completed</p>
              </div>
            ) : inCall && roomUrl && doctorToken ? (
              <>
                <VideoRoom
                  roomUrl={roomUrl}
                  token={doctorToken}
                  onLeave={() => setInCall(false)}
                />
                <p className="text-xs text-gray-400 mt-2 text-center">
                  Worker join link sent. Worker token active.
                </p>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-4xl mb-3">📹</p>
                <p className="text-sm text-gray-500 mb-4">
                  {status === 'ACCEPTED'
                    ? 'Click below to start the video consultation'
                    : 'Accept the case first to start a call'}
                </p>
                <Button
                  onClick={handleStartCall}
                  loading={callLoading}
                  disabled={status === 'PENDING'}
                  className="w-full"
                >
                  {callLoading ? 'Creating room...' : '📹 Start Video Call'}
                </Button>
              </div>
            )}
          </Card>

          {/* Notes form */}
          {status !== 'COMPLETED' ? (
            <Card title="📝 Consultation Notes">
              <form onSubmit={handleSubmit(handleComplete)} noValidate>
                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Clinical Notes *
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Describe findings, patient condition, immediate actions taken..."
                    className={`w-full px-3 py-2 border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500
                      ${errors.doctorNotes ? 'border-red-400' : 'border-gray-300'}`}
                    {...register('doctorNotes', { required: 'Clinical notes are required' })}
                  />
                  {errors.doctorNotes && (
                    <p className="text-xs text-red-600 mt-0.5">{errors.doctorNotes.message}</p>
                  )}
                </div>

                <div className="mb-3">
                  <label className="block text-xs font-medium text-gray-500 mb-1">Diagnosis</label>
                  <textarea
                    rows={2}
                    placeholder="e.g. Severe Pre-eclampsia with superimposed anaemia"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    {...register('diagnosis')}
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Action Plan *
                  </label>
                  <textarea
                    rows={3}
                    placeholder="1. Immediate referral to CEmOC&#10;2. IV MgSO4 prophylaxis&#10;3. Blood transfusion"
                    className={`w-full px-3 py-2 border rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500
                      ${errors.actionPlan ? 'border-red-400' : 'border-gray-300'}`}
                    {...register('actionPlan', { required: 'Action plan is required' })}
                  />
                  {errors.actionPlan && (
                    <p className="text-xs text-red-600 mt-0.5">{errors.actionPlan.message}</p>
                  )}
                </div>

                <Button type="submit" loading={submitting} className="w-full">
                  ✅ Complete Consultation
                </Button>
              </form>
            </Card>
          ) : (
            /* Show completed notes */
            <Card title="✅ Consultation Notes (Completed)">
              <InfoRow label="Notes"       value={doctorNotes} />
              <InfoRow label="Diagnosis"   value={diagnosis} />
              <InfoRow label="Action Plan" value={actionPlan} />
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <h3 className="font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-100">{title}</h3>
      {children}
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-xs text-gray-400">{label}</span>
      <span className="text-sm font-medium text-gray-800 text-right max-w-[60%]">
        {value || '—'}
      </span>
    </div>
  );
}
```

---

## src/pages/doctor/DoctorHistoryPage.jsx

```jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDoctorHistory } from '../../api/consultationApi';
import { useApi } from '../../hooks/useApi';
import PriorityBadge from '../../components/doctor/PriorityBadge';
import Spinner from '../../components/ui/Spinner';
import ErrorAlert from '../../components/ui/ErrorAlert';

export default function DoctorHistoryPage() {
  const navigate = useNavigate();
  const { execute, data: history, loading, error } = useApi(getDoctorHistory);

  useEffect(() => { execute(); }, []);

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">My Consultation History</h2>
        <p className="text-sm text-gray-500">{history?.length || 0} completed consultations</p>
      </div>

      <ErrorAlert message={error} />

      {loading && <div className="flex justify-center py-12"><Spinner size="lg" /></div>}

      {!loading && history?.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <div className="text-5xl mb-3">📂</div>
          <p>No completed consultations yet.</p>
        </div>
      )}

      <div className="space-y-3">
        {history?.map((c) => (
          <div
            key={c.consultationId}
            className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between cursor-pointer hover:shadow-sm transition-shadow"
            onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <PriorityBadge riskLevel={c.riskLevel} />
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium
                  ${c.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {c.status}
                </span>
              </div>
              <p className="text-sm font-semibold text-gray-900">{c.patientName || 'Patient'}</p>
              <p className="text-xs text-gray-500">
                {c.patientAge ? `Age ${c.patientAge}` : ''}
                {c.gestationalWeeks ? ` • ${c.gestationalWeeks}w` : ''}
                {c.district ? ` • ${c.district}` : ''}
              </p>
              {c.completedAt && (
                <p className="text-xs text-gray-400 mt-0.5">
                  Completed: {new Date(c.completedAt).toLocaleString('en-IN')}
                </p>
              )}
            </div>
            <span className="text-blue-400 text-xs font-medium">View →</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## src/App.jsx — UPDATE with Doctor Routes

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider }       from './context/AuthContext';
import { DoctorAuthProvider } from './context/DoctorAuthContext';
import ProtectedRoute         from './routes/ProtectedRoute';
import DoctorProtectedRoute   from './routes/DoctorProtectedRoute';
import AppLayout              from './components/layout/AppLayout';
import DoctorLayout           from './components/doctor/DoctorLayout';

// Worker pages (existing)
import LoginPage          from './pages/LoginPage';
import SignupPage         from './pages/SignupPage';
import DashboardPage      from './pages/DashboardPage';
import PatientListPage    from './pages/PatientListPage';
import PatientCreatePage  from './pages/PatientCreatePage';
import PatientDetailPage  from './pages/PatientDetailPage';
import AncVisitFormPage   from './pages/AncVisitFormPage';
import VisitResultPage    from './pages/VisitResultPage';

// Doctor pages (new)
import DoctorLoginPage            from './pages/doctor/DoctorLoginPage';
import DoctorSignupPage           from './pages/doctor/DoctorSignupPage';
import DoctorQueuePage            from './pages/doctor/DoctorQueuePage';
import ConsultationDetailPage     from './pages/doctor/ConsultationDetailPage';
import DoctorHistoryPage          from './pages/doctor/DoctorHistoryPage';

export default function App() {
  return (
    <AuthProvider>
      <DoctorAuthProvider>
        <BrowserRouter>
          <Routes>

            {/* ── ANC Worker routes ──────────────────────────────────── */}
            <Route path="/login"  element={<LoginPage />}  />
            <Route path="/signup" element={<SignupPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/dashboard"             element={<DashboardPage />}      />
                <Route path="/patients"              element={<PatientListPage />}    />
                <Route path="/patients/new"          element={<PatientCreatePage />}  />
                <Route path="/patients/:id"          element={<PatientDetailPage />}  />
                <Route path="/visits/new/:patientId" element={<AncVisitFormPage />}   />
                <Route path="/visits/:visitId"       element={<VisitResultPage />}    />
              </Route>
            </Route>

            {/* ── Doctor routes ──────────────────────────────────────── */}
            <Route path="/doctor/login"  element={<DoctorLoginPage />}  />
            <Route path="/doctor/signup" element={<DoctorSignupPage />} />

            <Route element={<DoctorProtectedRoute />}>
              <Route element={<DoctorLayout />}>
                <Route path="/doctor/queue"                         element={<DoctorQueuePage />}         />
                <Route path="/doctor/consultations/:consultationId" element={<ConsultationDetailPage />}  />
                <Route path="/doctor/history"                       element={<DoctorHistoryPage />}        />
              </Route>
            </Route>

            {/* ── Defaults ───────────────────────────────────────────── */}
            <Route path="/"   element={<Navigate to="/login"        replace />} />
            <Route path="*"   element={<Navigate to="/login"        replace />} />

          </Routes>
        </BrowserRouter>
      </DoctorAuthProvider>
    </AuthProvider>
  );
}
```

---

## Install @daily-co/daily-js

```bash
npm install @daily-co/daily-js
```

---

## Complete System Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│  ANC WORKER (React)                                                    │
│    Submits 7-step ANC form  →  POST /api/anc/register-visit           │
│                                        ↓                               │
│                              Spring Boot saves visit                   │
│                              Calls FastAPI → isHighRisk=true           │
│                                        ↓                               │
│                              AUTO: ConsultationEntity created          │
│                                    status=PENDING                      │
│                                    priorityScore=100 (CRITICAL)        │
│                                        ↓                               │
├────────────────────────────────────────────────────────────────────────┤
│  DOCTOR (React — /doctor/queue)                                        │
│    Sees CRITICAL card at top of queue  (auto-refreshes 30s)           │
│    Clicks "Accept Case"  →  POST /api/consultations/{id}/accept        │
│                                        ↓                               │
│                              status = ACCEPTED                         │
│                                        ↓                               │
│    Opens ConsultationDetailPage                                        │
│      - Reads patient info, AI risks, explanation                       │
│      - Reviews detectedRisks[], recommendation                         │
│                                        ↓                               │
│    Clicks "Start Video Call"  →  POST /api/consultations/{id}/start-call│
│                                        ↓                               │
│                              VideoSessionService.createRoom()          │
│                              Daily.co API → room URL + tokens          │
│                              status = IN_PROGRESS                      │
│                                        ↓                               │
│    Daily.co video embed loads in browser                               │
│    Worker receives workerToken (can join from their browser)           │
│                                        ↓                               │
│    After consultation:                                                 │
│    Doctor fills Notes + Diagnosis + Action Plan                        │
│    Clicks "Complete"  →  POST /api/consultations/{id}/complete         │
│                                        ↓                               │
│                              status = COMPLETED                        │
│                              doctorNotes saved to DB                   │
├────────────────────────────────────────────────────────────────────────┤
│  ANC WORKER (React — PatientDetailPage)                                │
│    Sees consultation card under patient                                │
│    Reads doctor's notes, diagnosis, action plan                        │
│    Knows to arrange referral / follow PMSMA protocol                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Summary — All New Files

### Spring Boot (Backend)
| File | Purpose |
|------|---------|
| `DoctorEntity.java` | Doctor account, implements UserDetails, ROLE_DOCTOR |
| `ConsultationEntity.java` | Consultation record, status lifecycle, video tokens |
| `DoctorRepository.java` | findByPhone, findAvailableByDistrict |
| `ConsultationRepository.java` | Priority queue query, exists checks |
| `DoctorSignupRequestDTO.java` | Doctor signup fields |
| `DoctorLoginRequestDTO.java` | `{ phone, password }` |
| `DoctorAuthResponseDTO.java` | Token + role + doctor info |
| `ConsultationResponseDTO.java` | Full enriched consultation (patient + visit + risk) |
| `ConsultationNotesRequestDTO.java` | `{ doctorNotes, diagnosis, actionPlan }` |
| `DoctorAuthService.java` | Signup + login logic |
| `ConsultationService.java` | createFromVisit, queue, accept, startCall, complete |
| `VideoSessionService.java` | Daily.co room creation + token generation |
| `DoctorAuthController.java` | `/api/doctor/auth/*` endpoints |
| `ConsultationController.java` | `/api/consultations/*` endpoints |
| **Updated:** `CustomUserDetailsService` | Now checks both workers + doctors tables |
| **Updated:** `SecurityConfig` | Added ROLE_DOCTOR rules |
| **Updated:** `JwtService` | generateToken() now accepts role param |
| **Updated:** `AncVisitService` | Triggers consultation on isHighRisk=true |

### React (Frontend)
| File | Purpose |
|------|---------|
| `doctorApi.js` | signup, login, getMe |
| `consultationApi.js` | queue, accept, startCall, complete, history |
| `DoctorAuthContext.jsx` | Doctor auth state + localStorage |
| `useDoctorAuth.js` | Context hook |
| `DoctorProtectedRoute.jsx` | Redirect to /doctor/login if not authenticated |
| `DoctorLayout.jsx` | Doctor portal sidebar + layout |
| `PriorityBadge.jsx` | CRITICAL (pulsing red) / HIGH / MEDIUM badges |
| `ConsultationCard.jsx` | Queue item with Accept button + risk tags |
| `VideoRoom.jsx` | Daily.co iframe embed component |
| `DoctorLoginPage.jsx` | Login form |
| `DoctorSignupPage.jsx` | Signup form |
| `DoctorQueuePage.jsx` | Priority queue, grouped by CRITICAL/HIGH/MEDIUM |
| `ConsultationDetailPage.jsx` | Full case view + video call + notes form |
| `DoctorHistoryPage.jsx` | Past completed consultations |
| **Updated:** `App.jsx` | Added all `/doctor/*` routes |

# DTO ↔ Entity Mapping Documentation

## Overview
This document maps all Request DTOs, Response DTOs, and Entity classes, showing how data flows through the application layers.

---

## 1. WORKER AUTHENTICATION

### Entity: `AncWorkerEntity`
```java
@Entity
@Table(name = "anc_workers")
class AncWorkerEntity {
    UUID id;
    String fullName;
    String phone;  // Unique, used for login
    String email;
    String passwordHash;
    String healthCenter;
    String district;
    String role = "WORKER";
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Request DTO: `SignupRequestDTO`
```java
class SignupRequestDTO {
    String fullName;
    String phone;      // @Pattern ^[6-9]\\d{9}$
    String email;      // @Email
    String password;   // @Size min=8
    String healthCenter;
    String district;
}
```

### Request DTO: `LoginRequestDTO`
```java
class LoginRequestDTO {
    String phone;      // @Pattern ^[6-9]\\d{9}$
    String password;
}
```

### Response DTO: `AuthResponseDTO`
```java
class AuthResponseDTO {
    String token;      // JWT
    UUID workerId;
    String fullName;
    String phone;
    String email;
    String healthCenter;
    String district;
    String message;
}
```

### Response DTO: `WorkerProfileResponseDTO`
```java
class WorkerProfileResponseDTO {
    UUID workerId;
    String fullName;
    String phone;
    String email;
    String healthCenter;
    String district;
    LocalDateTime createdAt;
}
```

### Mapping Flow (Signup)
```
SignupRequestDTO → AuthService.signup()
  ├─ Create AncWorkerEntity
  │  ├─ fullName = request.fullName
  │  ├─ phone = request.phone
  │  ├─ email = request.email
  │  ├─ passwordHash = passwordEncoder.encode(request.password)
  │  ├─ healthCenter = request.healthCenter
  │  ├─ district = request.district
  │  └─ role = "WORKER"
  ├─ Save to database
  ├─ Generate JWT token
  └─ Return AuthResponseDTO
     ├─ token = jwtService.generateToken(worker)
     ├─ workerId = worker.id
     ├─ fullName = worker.fullName
     ├─ phone = worker.phone
     ├─ email = worker.email
     ├─ healthCenter = worker.healthCenter
     ├─ district = worker.district
     └─ message = "Signup successful"
```

---

## 2. DOCTOR AUTHENTICATION

### Entity: `DoctorEntity`
```java
@Entity
@Table(name = "doctors")
class DoctorEntity {
    String id;         // UUID as String
    String fullName;
    String phone;      // Unique, used for login
    String email;
    String passwordHash;
    String specialization;
    String hospital;
    String district;
    String registrationNo;
    Boolean isAvailable = true;
    String role = "DOCTOR";
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Request DTO: `DoctorSignupRequestDTO`
```java
class DoctorSignupRequestDTO {
    String fullName;
    String phone;           // @Pattern ^[6-9]\\d{9}$
    String email;           // @Email
    String password;        // @Size min=8
    String specialization;
    String hospital;
    String district;
    String registrationNo;
}
```

### Request DTO: `DoctorLoginRequestDTO`
```java
class DoctorLoginRequestDTO {
    String phone;      // @Pattern ^[6-9]\\d{9}$
    String password;
}
```

### Response DTO: `DoctorAuthResponseDTO`
```java
class DoctorAuthResponseDTO {
    String token;           // JWT
    String role = "DOCTOR";
    String doctorId;
    String fullName;
    String phone;
    String email;
    String specialization;
    String hospital;
    String district;
    String registrationNo;
    Boolean isAvailable;
    String message;
}
```

### Mapping Flow (Signup)
```
DoctorSignupRequestDTO → DoctorAuthService.signup()
  ├─ Create DoctorEntity
  │  ├─ id = UUID.randomUUID().toString()
  │  ├─ fullName = request.fullName
  │  ├─ phone = request.phone
  │  ├─ email = request.email
  │  ├─ passwordHash = passwordEncoder.encode(request.password)
  │  ├─ specialization = request.specialization
  │  ├─ hospital = request.hospital
  │  ├─ district = request.district
  │  ├─ registrationNo = request.registrationNo
  │  ├─ isAvailable = true
  │  └─ role = "DOCTOR"
  ├─ Save to database
  ├─ Generate JWT token
  └─ Return DoctorAuthResponseDTO
     ├─ token = jwtService.generateToken(doctor)
     ├─ role = "DOCTOR"
     ├─ doctorId = doctor.id
     ├─ fullName = doctor.fullName
     ├─ phone = doctor.phone
     ├─ email = doctor.email
     ├─ specialization = doctor.specialization
     ├─ hospital = doctor.hospital
     ├─ district = doctor.district
     ├─ registrationNo = doctor.registrationNo
     ├─ isAvailable = doctor.isAvailable
     └─ message = "Doctor registered successfully"
```

---

## 3. PATIENT MANAGEMENT

### Entity: `PatientEntity`
```java
@Entity
@Table(name = "patients")
class PatientEntity {
    UUID id;
    AncWorkerEntity worker;  // ManyToOne relationship
    String fullName;
    String phone;
    Integer age;
    String address;
    String village;
    String district;
    LocalDate lmpDate;
    LocalDate eddDate;
    String bloodGroup;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Request DTO: `PatientRequestDTO`
```java
class PatientRequestDTO {
    String fullName;
    String phone;      // @Pattern ^[6-9]\\d{9}$
    Integer age;       // @Min 1
    String address;
    String village;
    String district;
    LocalDate lmpDate;
    LocalDate eddDate;
    String bloodGroup;
}
```

### Response DTO: `PatientResponseDTO`
```java
class PatientResponseDTO {
    UUID patientId;
    UUID workerId;
    String fullName;
    String phone;
    Integer age;
    String address;
    String village;
    String district;
    LocalDate lmpDate;
    LocalDate eddDate;
    String bloodGroup;
    LocalDateTime createdAt;
}
```

### Mapping Flow (Create Patient)
```
PatientRequestDTO + workerId → PatientService.createPatient()
  ├─ Load AncWorkerEntity by workerId
  ├─ Create PatientEntity
  │  ├─ worker = workerEntity
  │  ├─ fullName = request.fullName
  │  ├─ phone = request.phone
  │  ├─ age = request.age
  │  ├─ address = request.address
  │  ├─ village = request.village
  │  ├─ district = request.district
  │  ├─ lmpDate = request.lmpDate
  │  ├─ eddDate = request.eddDate
  │  └─ bloodGroup = request.bloodGroup
  ├─ Save to database
  └─ Return PatientResponseDTO
     ├─ patientId = patient.id
     ├─ workerId = patient.worker.id
     ├─ fullName = patient.fullName
     ├─ phone = patient.phone
     ├─ age = patient.age
     ├─ address = patient.address
     ├─ village = patient.village
     ├─ district = patient.district
     ├─ lmpDate = patient.lmpDate
     ├─ eddDate = patient.eddDate
     ├─ bloodGroup = patient.bloodGroup
     └─ createdAt = patient.createdAt
```

---

## 4. ANC VISIT MANAGEMENT

### Entity: `AncVisitEntity`
```java
@Entity
@Table(name = "anc_visits")
class AncVisitEntity {
    String id;                    // UUID as String
    String patientId;
    String patientName;
    String workerId;
    String phcId;
    String clinicalSummary;
    String riskLevel;             // LOW, MEDIUM, HIGH, CRITICAL
    Double riskScore;
    String aiAnalysis;
    List<String> recommendations;
    Boolean requiresConsultation;
    String consultationPriority;  // LOW, MEDIUM, HIGH, CRITICAL
    
    // Nested JSON fields (stored as JSON in database)
    StructuredDataDTO structuredData;
    
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Request DTO: `AncVisitRequestDTO`
```java
class AncVisitRequestDTO {
    String patientId;
    String patientName;
    String workerId;
    String phcId;
    String clinicalSummary;  // Optional, auto-generated if not provided
    StructuredDataDTO structuredData;  // @Valid @NotNull
}
```

### Nested DTO: `StructuredDataDTO`
```java
class StructuredDataDTO {
    Integer visitNumber;
    Integer gestationalAge;
    VitalsDTO vitals;
    CurrentSymptomsDTO currentSymptoms;
    MedicalHistoryDTO medicalHistory;
    ObstetricHistoryDTO obstetricHistory;
    LabReportsDTO labReports;
    PregnancyDetailsDTO pregnancyDetails;
}
```

### Response DTO: `AncVisitResponseDTO`
```java
class AncVisitResponseDTO {
    String visitId;
    String patientId;
    String riskLevel;
    Double riskScore;
    List<String> recommendations;
    Boolean requiresConsultation;
    String consultationPriority;
    String aiAnalysis;
    LocalDateTime timestamp;
}
```

### Mapping Flow (Register Visit)
```
AncVisitRequestDTO → AncVisitService.registerVisit()
  ├─ Generate clinical summary (if not provided)
  │  └─ ClinicalSummaryBuilder.build(structuredData)
  ├─ Call FastAPI for AI analysis
  │  ├─ Create FastApiRequestDTO
  │  │  ├─ patientId = request.patientId
  │  │  ├─ patientName = request.patientName
  │  │  ├─ clinicalSummary = generated summary
  │  │  └─ structuredData = request.structuredData
  │  └─ POST to http://localhost:8000/analyze
  ├─ Receive FastApiResponseDTO
  │  ├─ riskLevel
  │  ├─ riskScore
  │  ├─ recommendations
  │  ├─ requiresConsultation
  │  ├─ consultationPriority
  │  └─ aiAnalysis
  ├─ Create AncVisitEntity
  │  ├─ id = UUID.randomUUID().toString()
  │  ├─ patientId = request.patientId
  │  ├─ patientName = request.patientName
  │  ├─ workerId = request.workerId
  │  ├─ phcId = request.phcId
  │  ├─ clinicalSummary = generated summary
  │  ├─ structuredData = request.structuredData (as JSON)
  │  ├─ riskLevel = aiResponse.riskLevel
  │  ├─ riskScore = aiResponse.riskScore
  │  ├─ recommendations = aiResponse.recommendations
  │  ├─ requiresConsultation = aiResponse.requiresConsultation
  │  ├─ consultationPriority = aiResponse.consultationPriority
  │  └─ aiAnalysis = aiResponse.aiAnalysis
  ├─ Save to database
  ├─ If requiresConsultation = true
  │  └─ Create ConsultationEntity (auto-referral)
  └─ Return AncVisitResponseDTO
     ├─ visitId = visit.id
     ├─ patientId = visit.patientId
     ├─ riskLevel = visit.riskLevel
     ├─ riskScore = visit.riskScore
     ├─ recommendations = visit.recommendations
     ├─ requiresConsultation = visit.requiresConsultation
     ├─ consultationPriority = visit.consultationPriority
     ├─ aiAnalysis = visit.aiAnalysis
     └─ timestamp = visit.createdAt
```

---

## 5. CONSULTATION MANAGEMENT

### Entity: `ConsultationEntity`
```java
@Entity
@Table(name = "consultations")
class ConsultationEntity {
    String id;                    // UUID as String
    String patientId;
    String patientName;
    String visitId;
    String doctorId;              // Nullable until accepted
    String doctorName;            // Nullable until accepted
    String status;                // PENDING, ACCEPTED, IN_PROGRESS, COMPLETED
    String priority;              // CRITICAL, HIGH, MEDIUM, LOW
    String riskLevel;
    Double riskScore;
    LocalDateTime scheduledDateTime;
    LocalDateTime completedDateTime;
    String doctorNotes;
    String diagnosis;
    String actionPlan;
    String videoRoomUrl;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Request DTO: `ConsultationRequestDTO`
```java
class ConsultationRequestDTO {
    String patientId;
    String patientName;
    String visitId;
    String priority;      // CRITICAL, HIGH, MEDIUM, LOW
    String riskLevel;
    Double riskScore;
}
```

### Request DTO: `ConsultationNotesRequestDTO`
```java
class ConsultationNotesRequestDTO {
    String doctorNotes;
    String diagnosis;
    String actionPlan;
}
```

### Response DTO: `ConsultationResponseDTO`
```java
class ConsultationResponseDTO {
    String id;
    String patientId;
    String patientName;
    String visitId;
    String doctorId;
    String doctorName;
    String status;
    String priority;
    String riskLevel;
    Double riskScore;
    LocalDateTime scheduledDateTime;
    LocalDateTime completedDateTime;
    String doctorNotes;
    String diagnosis;
    String actionPlan;
    String videoRoomUrl;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
}
```

### Mapping Flow (Accept Consultation)
```
consultationId + doctorId → ConsultationService.accept()
  ├─ Load ConsultationEntity by id
  ├─ Validate status = PENDING
  ├─ Load DoctorEntity by doctorId
  ├─ Update ConsultationEntity
  │  ├─ doctorId = doctor.id
  │  ├─ doctorName = doctor.fullName
  │  ├─ status = "ACCEPTED"
  │  └─ updatedAt = now()
  ├─ Save to database
  └─ Return ConsultationResponseDTO
     ├─ id = consultation.id
     ├─ patientId = consultation.patientId
     ├─ patientName = consultation.patientName
     ├─ visitId = consultation.visitId
     ├─ doctorId = consultation.doctorId
     ├─ doctorName = consultation.doctorName
     ├─ status = consultation.status
     ├─ priority = consultation.priority
     ├─ riskLevel = consultation.riskLevel
     ├─ riskScore = consultation.riskScore
     ├─ scheduledDateTime = consultation.scheduledDateTime
     ├─ completedDateTime = consultation.completedDateTime
     ├─ doctorNotes = consultation.doctorNotes
     ├─ diagnosis = consultation.diagnosis
     ├─ actionPlan = consultation.actionPlan
     ├─ videoRoomUrl = consultation.videoRoomUrl
     ├─ createdAt = consultation.createdAt
     └─ updatedAt = consultation.updatedAt
```

### Mapping Flow (Complete Consultation)
```
consultationId + doctorId + ConsultationNotesRequestDTO → ConsultationService.complete()
  ├─ Load ConsultationEntity by id
  ├─ Validate status = IN_PROGRESS
  ├─ Validate doctorId matches
  ├─ Update ConsultationEntity
  │  ├─ doctorNotes = request.doctorNotes
  │  ├─ diagnosis = request.diagnosis
  │  ├─ actionPlan = request.actionPlan
  │  ├─ status = "COMPLETED"
  │  ├─ completedDateTime = now()
  │  └─ updatedAt = now()
  ├─ Save to database
  └─ Return ConsultationResponseDTO (full consultation data)
```

---

## 6. FASTAPI INTEGRATION

### Request DTO: `FastApiRequestDTO`
```java
class FastApiRequestDTO {
    String patientId;
    String patientName;
    String clinicalSummary;
    StructuredDataDTO structuredData;
}
```

### Response DTO: `FastApiResponseDTO`
```java
class FastApiResponseDTO {
    String riskLevel;             // LOW, MEDIUM, HIGH, CRITICAL
    Double riskScore;             // 0.0 - 1.0
    List<String> recommendations;
    Boolean requiresConsultation;
    String consultationPriority;  // LOW, MEDIUM, HIGH, CRITICAL
    String aiAnalysis;
}
```

### Mapping Flow
```
AncVisitRequestDTO → FastApiClient.analyzeVisit()
  ├─ Create FastApiRequestDTO
  │  ├─ patientId = visitRequest.patientId
  │  ├─ patientName = visitRequest.patientName
  │  ├─ clinicalSummary = generated summary
  │  └─ structuredData = visitRequest.structuredData
  ├─ POST to http://localhost:8000/analyze
  └─ Receive FastApiResponseDTO
     ├─ riskLevel
     ├─ riskScore
     ├─ recommendations
     ├─ requiresConsultation
     ├─ consultationPriority
     └─ aiAnalysis
```

---

## 7. KEY MAPPING PATTERNS

### Pattern 1: Request → Entity (Create)
```
RequestDTO → Service.create()
  ├─ Validate request
  ├─ Map DTO fields to Entity fields
  ├─ Set auto-generated fields (id, timestamps)
  ├─ Save entity
  └─ Map Entity to ResponseDTO
```

### Pattern 2: Entity → Response (Read)
```
Service.get() → Entity
  ├─ Load entity from database
  ├─ Map Entity fields to ResponseDTO fields
  └─ Return ResponseDTO
```

### Pattern 3: Request + Entity → Entity (Update)
```
RequestDTO + entityId → Service.update()
  ├─ Load existing entity
  ├─ Validate update permissions
  ├─ Update entity fields from DTO
  ├─ Save entity
  └─ Map Entity to ResponseDTO
```

### Pattern 4: Nested DTOs
```
ParentDTO {
  ChildDTO child;
}

Stored as JSON in database:
Entity {
  @Column(columnDefinition = "jsonb")
  String childJson;
}
```

---

## 8. VALIDATION ANNOTATIONS

### Common Validations
- `@NotBlank` - String must not be null or empty
- `@NotNull` - Field must not be null
- `@Email` - Must be valid email format
- `@Pattern(regexp="...")` - Must match regex pattern
- `@Size(min=X, max=Y)` - String length constraints
- `@Min(value=X)` - Numeric minimum value
- `@Valid` - Validate nested DTO

### Phone Number Pattern
```java
@Pattern(regexp = "^[6-9]\\d{9}$")
// Validates 10-digit Indian mobile number starting with 6-9
```

---

## 9. JSON PROPERTY MAPPING

All DTOs use `@JsonProperty` to ensure consistent field naming between Java (camelCase) and JSON (camelCase):

```java
@JsonProperty("fullName")
private String fullName;
```

This ensures:
- Frontend sends: `{ "fullName": "..." }`
- Backend receives: `fullName` field
- Backend sends: `{ "fullName": "..." }`
- Frontend receives: `fullName` property

---

## SUMMARY

✅ All Request DTOs validated with Jakarta Validation  
✅ All Entity classes use JPA annotations  
✅ All Response DTOs use Builder pattern  
✅ All mappings preserve data integrity  
✅ All nested DTOs properly validated  
✅ All JSON fields properly annotated  
✅ All relationships properly mapped (ManyToOne, etc.)

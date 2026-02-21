# ANC Worker Authentication Module - Implementation Complete

## Overview

Successfully implemented JWT-based authentication and patient management for the ANC service. The module adds secure worker authentication, patient registration, and data isolation capabilities.

## What Was Implemented

### 1. Dependencies & Configuration
- ✅ Spring Security starter
- ✅ JWT libraries (jjwt-api, jjwt-impl, jjwt-jackson v0.12.3)
- ✅ JWT configuration (secret key, 24-hour expiration)
- ✅ BCrypt password encoder (strength 12)

### 2. Database Schema
- ✅ `anc_workers` table - Worker authentication and profiles
- ✅ `patients` table - Patient demographic and pregnancy data
- ✅ Indexes on phone, email, worker_id, district columns
- ✅ Automatic timestamp management with triggers

### 3. Entity Layer
- ✅ `AncWorkerEntity` - Implements Spring Security UserDetails
- ✅ `PatientEntity` - Patient records with worker relationship

### 4. Repository Layer
- ✅ `AncWorkerRepository` - Worker lookup by phone, duplicate checking
- ✅ `PatientRepository` - Worker-scoped patient queries

### 5. DTO Layer
- ✅ `SignupRequestDTO` - Worker registration with validation
- ✅ `LoginRequestDTO` - Login credentials with validation
- ✅ `AuthResponseDTO` - JWT token and worker profile response
- ✅ `PatientRequestDTO` - Patient creation with validation
- ✅ `PatientResponseDTO` - Patient details response

### 6. Service Layer
- ✅ `JwtService` - Token generation, validation, and parsing
- ✅ `CustomUserDetailsService` - Spring Security user loading
- ✅ `AuthService` - Signup, login, and profile operations
- ✅ `PatientService` - Patient CRUD with data isolation

### 7. Security Configuration
- ✅ `JwtAuthenticationFilter` - JWT token validation filter
- ✅ `SecurityConfig` - Spring Security configuration
  - Stateless session management
  - Public endpoints: /api/auth/signup, /api/auth/login
  - Protected endpoints: all others require JWT
  - CSRF disabled for REST API
  - CORS enabled for development

### 8. Controller Layer
- ✅ `AuthController` - Signup, login, profile endpoints
- ✅ `PatientController` - Patient CRUD endpoints
- ✅ Existing `AncVisitController` - Now protected by JWT

### 9. Exception Handling
- ✅ BadCredentialsException → HTTP 401
- ✅ DisabledException → HTTP 403
- ✅ LockedException → HTTP 403
- ✅ UsernameNotFoundException → HTTP 401
- ✅ Validation errors → HTTP 400

## API Endpoints

### Authentication Endpoints (Public)

**POST /api/auth/signup**
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d @test-signup.json
```

**POST /api/auth/login**
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d @test-login.json
```

**GET /api/auth/me** (Protected)
```bash
curl -X GET http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Patient Endpoints (Protected)

**POST /api/patients**
```bash
curl -X POST http://localhost:8080/api/patients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test-patient.json
```

**GET /api/patients**
```bash
curl -X GET http://localhost:8080/api/patients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**GET /api/patients/{id}**
```bash
curl -X GET http://localhost:8080/api/patients/{PATIENT_ID} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### ANC Visit Endpoints (Now Protected)

**POST /api/anc/register-visit**
```bash
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test-request.json
```

## How to Run

### 1. Start the Application
```bash
cd Backend
java -jar target/anc-service-1.0.0.jar
```

The application will:
- Connect to PostgreSQL database "NeoSure"
- Automatically create `anc_workers` and `patients` tables
- Start on port 8080

### 2. Test Authentication Flow

**Step 1: Signup**
```bash
curl -X POST http://localhost:8080/api/auth/signup \
  -H "Content-Type: application/json" \
  -d @test-signup.json
```

Response includes JWT token:
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "workerId": "uuid-here",
  "fullName": "Anjali Devi",
  "phone": "9876543210",
  "email": "anjali@phc.in",
  "healthCenter": "PHC Angondhalli",
  "district": "Bangalore Rural",
  "message": "Worker registered successfully"
}
```

**Step 2: Login**
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d @test-login.json
```

**Step 3: Create Patient**
```bash
curl -X POST http://localhost:8080/api/patients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test-patient.json
```

**Step 4: List Patients**
```bash
curl -X GET http://localhost:8080/api/patients \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Features

### JWT Token
- **Algorithm**: HMAC-SHA256
- **Expiration**: 24 hours
- **Claims**: phone (subject), workerId (custom claim)
- **Storage**: Client stores in localStorage

### Password Security
- **Hashing**: BCrypt with strength 12
- **Validation**: Minimum 8 characters
- **Storage**: Only hashed passwords stored in database

### Data Isolation
- Workers can only access their own patients
- Worker ID extracted from JWT token (not request body)
- Repository queries filtered by worker ID
- Access attempts to other workers' data are logged and rejected

### Request Validation
- Phone number: 10-digit Indian mobile (starts with 6-9)
- Email: Valid email format
- Required fields: Validated with @NotBlank, @NotNull
- Custom validation messages for user-friendly errors

## Test Files

- `test-signup.json` - Worker registration
- `test-login.json` - Worker login
- `test-patient.json` - Patient creation
- `test-request.json` - ANC visit submission (existing)

## Database Tables

### anc_workers
- id (UUID, PK)
- full_name
- phone (unique)
- email (unique)
- password_hash (BCrypt)
- health_center
- district
- is_active
- created_at, updated_at

### patients
- id (UUID, PK)
- worker_id (FK to anc_workers)
- full_name
- phone
- age
- address, village, district
- lmp_date, edd_date
- blood_group
- created_at, updated_at

## Next Steps

1. **Start the application**: `java -jar target/anc-service-1.0.0.jar`
2. **Test signup**: Use test-signup.json
3. **Test login**: Use test-login.json
4. **Create patients**: Use test-patient.json with JWT token
5. **Submit ANC visits**: Use test-request.json with JWT token

## Notes

- Tables are created automatically by Spring Boot (ddl-auto: update)
- JWT tokens expire after 24 hours
- All endpoints except /api/auth/signup and /api/auth/login require authentication
- CORS is enabled for all origins (development mode)
- Logging is set to DEBUG level for troubleshooting

## Implementation Status

✅ All 14 tasks completed
✅ Build successful (mvn clean package)
✅ No compilation errors
✅ Ready for testing

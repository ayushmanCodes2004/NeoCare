# ANC Service - Spring Boot Backend

## Overview
Spring Boot 3.2 REST API for Antenatal Care (ANC) patient registration with AI-powered risk assessment.

## Tech Stack
- Java 17
- Spring Boot 3.2.0
- PostgreSQL (with JSONB support)
- Lombok
- Jackson (JSON processing)
- Hypersistence Utils (JSONB mapping)

## Architecture
```
React → Spring Boot → PostgreSQL
              ↓
         FastAPI (AI Risk Analysis)
```

## Prerequisites
1. Java 17+
2. Maven 3.6+
3. PostgreSQL 12+
4. FastAPI service running on http://localhost:8000

## Database Setup
```bash
# Create database
psql -U postgres
CREATE DATABASE anc_db;
\c anc_db;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

# Run schema
psql -U postgres -d anc_db -f src/main/resources/schema.sql
```

## Configuration
Update `src/main/resources/application.yml`:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/anc_db
    username: postgres
    password: yourpassword

fastapi:
  base-url: http://localhost:8000
  api-key: your-fastapi-secret-key
```

## Build & Run
```bash
# Build
mvn clean install

# Run
mvn spring-boot:run

# Or run JAR
java -jar target/anc-service-1.0.0.jar
```

Server starts on: http://localhost:8080

## API Endpoints

### 1. Register Visit
```http
POST /api/anc/register-visit
Content-Type: application/json

{
  "patientId": "P12345",
  "workerId": "W001",
  "phcId": "PHC001",
  "structured_data": {
    "patient_info": {
      "age": 28,
      "gestationalWeeks": 32
    },
    "vitals": {
      "bpSystolic": 165,
      "bpDiastolic": 110
    }
    // ... more fields
  }
}
```

### 2. Get Visit by ID
```http
GET /api/anc/visits/{visitId}
```

### 3. Get Patient Visits
```http
GET /api/anc/patients/{patientId}/visits
```

### 4. Get High Risk Visits
```http
GET /api/anc/visits/high-risk
```

## Data Flow
1. React sends visit data
2. Spring Boot auto-generates clinical summary
3. Saves to PostgreSQL (status=REGISTERED)
4. Calls FastAPI for AI risk analysis
5. Updates DB with AI results (status=AI_ANALYZED)
6. Returns response to React

## Project Structure
```
src/main/java/com/anc/
├── AncServiceApplication.java
├── controller/
│   └── AncVisitController.java
├── service/
│   ├── AncVisitService.java
│   └── ClinicalSummaryBuilder.java
├── client/
│   └── FastApiClient.java
├── entity/
│   └── AncVisitEntity.java
├── repository/
│   └── AncVisitRepository.java
├── mapper/
│   └── AncVisitMapper.java
├── dto/
│   └── [13 DTO files]
├── exception/
│   ├── FastApiException.java
│   └── GlobalExceptionHandler.java
└── config/
    ├── RestTemplateConfig.java
    └── JacksonConfig.java
```

## Testing
```bash
# Test registration endpoint
curl -X POST http://localhost:8080/api/anc/register-visit \
  -H "Content-Type: application/json" \
  -d @test-payload.json
```

## Error Handling
- Validation errors: 400 Bad Request
- FastAPI unavailable: 503 Service Unavailable (visit still saved)
- Server errors: 500 Internal Server Error

## Notes
- Clinical summary is auto-generated if not provided
- Visit is saved even if AI analysis fails
- CORS enabled for all origins (restrict in production)
- Uses JSONB for flexible structured data storage

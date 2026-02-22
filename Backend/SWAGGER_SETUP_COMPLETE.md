# Swagger/OpenAPI Documentation Setup Complete

## ✅ What's Been Added

1. **Springdoc OpenAPI Dependency** - Added to `pom.xml`
2. **OpenAPI Configuration** - Created `OpenApiConfig.java`
3. **Swagger Annotations** - Added to `AuthController.java` as example

## 🚀 Access Swagger UI

After starting the backend, access Swagger UI at:

```
http://localhost:8080/swagger-ui/index.html
```

OpenAPI JSON specification:
```
http://localhost:8080/v3/api-docs
```

## 📋 API Documentation Overview

### Worker Authentication (`/api/auth`)
- `POST /api/auth/signup` - Register new ANC worker
- `POST /api/auth/login` - Worker login
- `GET /api/auth/me` - Get worker profile (requires JWT)

### Doctor Authentication (`/api/doctor/auth`)
- `POST /api/doctor/auth/signup` - Register new doctor
- `POST /api/doctor/auth/login` - Doctor login  
- `GET /api/doctor/auth/me` - Get doctor profile (requires JWT)

### Patient Management (`/api/patients`)
- `POST /api/patients` - Create new patient
- `GET /api/patients` - List all patients for worker
- `GET /api/patients/{id}` - Get patient details

### ANC Visits (`/api/anc`)
- `POST /api/anc/register-visit` - Register ANC visit with AI analysis
- `GET /api/anc/visits/{visitId}` - Get visit details
- `GET /api/anc/patients/{patientId}/visits` - Get patient visit history
- `GET /api/anc/visits/high-risk` - Get high-risk visits
- `GET /api/anc/visits/critical` - Get critical visits

### Consultations (`/api/consultations`)
- `GET /api/consultations/queue` - Get doctor's priority queue
- `GET /api/consultations/{id}` - Get consultation details
- `POST /api/consultations/{id}/accept` - Accept consultation
- `POST /api/consultations/{id}/start-call` - Start video call
- `POST /api/consultations/{id}/complete` - Complete consultation
- `GET /api/consultations/my-history` - Get doctor's history
- `GET /api/consultations/patient/{patientId}` - Get patient consultations

### WebRTC Signaling (`/ws`)
- WebSocket endpoint for video conferencing

## 🔐 Authentication

Most endpoints require JWT authentication. To use protected endpoints in Swagger:

1. Call `/api/auth/login` or `/api/doctor/auth/login`
2. Copy the `token` from the response
3. Click the "Authorize" button at the top of Swagger UI
4. Enter: `Bearer <your-token>`
5. Click "Authorize"

## 📝 Example Requests

### Worker Signup
```json
POST /api/auth/signup
{
  "fullName": "Priya Sharma",
  "phone": "9876543210",
  "email": "priya@health.gov.in",
  "password": "SecurePass123",
  "healthCenter": "Primary Health Center Bangalore",
  "district": "Bangalore Urban"
}
```

### Doctor Signup
```json
POST /api/doctor/auth/signup
{
  "fullName": "Dr. Rajesh Kumar",
  "phone": "9988776655",
  "email": "rajesh@hospital.in",
  "password": "DoctorPass123",
  "specialization": "Obstetrics & Gynaecology",
  "hospital": "District Hospital Bangalore",
  "district": "Bangalore Urban",
  "registrationNo": "KA-12345"
}
```

### Create Patient
```json
POST /api/patients
Authorization: Bearer <token>
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

### Register ANC Visit
```json
POST /api/anc/register-visit
Authorization: Bearer <token>
{
  "patientId": "550e8400-e29b-41d4-a716-446655440000",
  "patientName": "Lakshmi Devi",
  "workerId": "660e8400-e29b-41d4-a716-446655440001",
  "phcId": "PHC-BLR-001",
  "structured_data": {
    "visitNumber": 1,
    "gestationalAge": 12,
    "vitals": {
      "bloodPressure": "120/80",
      "weight": 58.5,
      "temperature": 98.6,
      "pulseRate": 72
    },
    "currentSymptoms": {
      "bleeding": false,
      "severePain": false,
      "fever": false,
      "reducedFetalMovement": false,
      "severeHeadache": false,
      "blurredVision": false,
      "swelling": false,
      "other": ""
    },
    "medicalHistory": {
      "diabetes": false,
      "hypertension": false,
      "heartDisease": false,
      "kidneyDisease": false,
      "thyroidDisorder": false,
      "previousCSection": false,
      "previousComplications": false,
      "other": ""
    },
    "obstetricHistory": {
      "gravida": 1,
      "para": 0,
      "abortion": 0,
      "livingChildren": 0,
      "previousPregnancyComplications": ""
    },
    "labReports": {
      "hemoglobin": 11.5,
      "bloodSugar": 95,
      "urineProtein": "Negative",
      "hiv": "Negative",
      "vdrl": "Negative",
      "hbsag": "Negative"
    },
    "pregnancyDetails": {
      "fundalHeight": 12,
      "fetalHeartRate": 140,
      "fetalPosition": "Cephalic",
      "placentaPosition": "Fundal",
      "amnioticFluid": "Normal"
    }
  }
}
```

### Accept Consultation
```json
POST /api/consultations/{id}/accept
Authorization: Bearer <doctor-token>
```

### Complete Consultation
```json
POST /api/consultations/{id}/complete
Authorization: Bearer <doctor-token>
{
  "doctorNotes": "Patient examined. Blood pressure slightly elevated. Advised rest and follow-up in 2 weeks.",
  "diagnosis": "Mild Gestational Hypertension",
  "actionPlan": "1. Monitor BP daily\n2. Reduce salt intake\n3. Adequate rest\n4. Follow-up visit in 2 weeks\n5. Emergency contact if severe headache or vision changes"
}
```

## 🎨 Swagger UI Features

- **Try it out** - Test endpoints directly from the browser
- **Request/Response examples** - See sample data for each endpoint
- **Schema definitions** - View all DTO structures
- **Authentication** - Built-in JWT token management
- **Response codes** - See all possible HTTP status codes
- **Download OpenAPI spec** - Export API documentation

## 🔧 Configuration

Swagger is configured in `OpenApiConfig.java` with:
- API title and description
- Version information
- Contact details
- License information
- Server URLs (dev and production)
- JWT Bearer authentication scheme

## 📦 Dependencies Added

```xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.3.0</version>
</dependency>
```

## 🚀 Next Steps

To add Swagger annotations to remaining controllers, follow the pattern in `AuthController.java`:

1. Add `@Tag` annotation to the controller class
2. Add `@Operation` annotation to each endpoint method
3. Add `@ApiResponses` with example responses
4. Add `@io.swagger.v3.oas.annotations.parameters.RequestBody` with examples
5. Add `@SecurityRequirement` for protected endpoints

## 📚 Additional Resources

- Springdoc OpenAPI: https://springdoc.org/
- OpenAPI Specification: https://swagger.io/specification/
- Swagger UI: https://swagger.io/tools/swagger-ui/

---

**Status:** ✅ Swagger UI is ready to use at http://localhost:8080/swagger-ui/index.html

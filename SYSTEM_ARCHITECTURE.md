# 🏗️ NeoSure System Architecture

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                   http://localhost:5173                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  LOVABLE FRONTEND                            │
│              React + TypeScript + Vite                       │
│                    Port: 5173                                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Worker     │  │    Doctor    │  │   Landing    │     │
│  │   Module     │  │    Module    │  │     Page     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         API Service (Axios + JWT)                     │  │
│  │  - Authentication interceptor                         │  │
│  │  - Auto-logout on 401                                 │  │
│  │  - Token management                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API (JSON)
                         │ Authorization: Bearer <JWT>
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  SPRING BOOT BACKEND                         │
│                    Port: 8080                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Security Layer                           │  │
│  │  - JWT Authentication Filter                          │  │
│  │  - Role-based Authorization (WORKER/DOCTOR)           │  │
│  │  - CORS Configuration                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Controllers  │  │   Services   │  │ Repositories │     │
│  │              │  │              │  │              │     │
│  │ - Auth       │  │ - Auth       │  │ - Worker     │     │
│  │ - Doctor     │  │ - Doctor     │  │ - Doctor     │     │
│  │ - Patient    │  │ - Patient    │  │ - Patient    │     │
│  │ - Visit      │  │ - Visit      │  │ - Visit      │     │
│  │ - Consult    │  │ - Consult    │  │ - Consult    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OpenAPI / Swagger                        │  │
│  │  - API Documentation                                  │  │
│  │  - Interactive Testing                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP POST
                         │ /analyze-risk
                         │
┌────────────────────────▼────────────────────────────────────┐
│              MEDICAL RAG PIPELINE                            │
│                  FastAPI + OpenAI                            │
│                    Port: 8000                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         AI Risk Assessment Engine                     │  │
│  │  - GPT-4o-mini for analysis                           │  │
│  │  - text-embedding-3-small for embeddings              │  │
│  │  - RAG (Retrieval Augmented Generation)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Risk Level Classification                     │  │
│  │  - LOW: Routine care                                  │  │
│  │  - MEDIUM: Increased monitoring                       │  │
│  │  - HIGH: Doctor consultation recommended              │  │
│  │  - CRITICAL: Immediate doctor consultation            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Risk Assessment Response
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  POSTGRESQL DATABASE                         │
│                    (or H2 for dev)                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Workers    │  │   Doctors    │  │   Patients   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  ANC Visits  │  │Consultations │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Worker Registers ANC Visit

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Worker  │────▶│Frontend │────▶│ Backend │────▶│   RAG   │
│  (UI)   │     │  (5173) │     │  (8080) │     │  (8000) │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │ Fill form     │               │               │
     │──────────────▶│               │               │
     │               │ POST /api/anc/│               │
     │               │ register-visit│               │
     │               │──────────────▶│               │
     │               │               │ POST /analyze │
     │               │               │──────────────▶│
     │               │               │               │
     │               │               │◀──────────────│
     │               │               │ Risk: HIGH    │
     │               │◀──────────────│               │
     │               │ Visit + Risk  │               │
     │◀──────────────│               │               │
     │ Show results  │               │               │
     │               │               │               │
     │               │               │ Create        │
     │               │               │ Consultation  │
     │               │               │──────────────▶│
     │               │               │               │
```

### 2. Doctor Accepts Consultation

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Doctor  │────▶│Frontend │────▶│ Backend │────▶│Database │
│  (UI)   │     │  (5173) │     │  (8080) │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │ View queue    │               │               │
     │──────────────▶│               │               │
     │               │ GET /api/     │               │
     │               │ consultations/│               │
     │               │ queue         │               │
     │               │──────────────▶│               │
     │               │               │ SELECT * FROM │
     │               │               │ consultations │
     │               │               │──────────────▶│
     │               │               │◀──────────────│
     │               │◀──────────────│               │
     │◀──────────────│               │               │
     │ Show queue    │               │               │
     │               │               │               │
     │ Click accept  │               │               │
     │──────────────▶│               │               │
     │               │ POST /api/    │               │
     │               │ consultations/│               │
     │               │ {id}/accept   │               │
     │               │──────────────▶│               │
     │               │               │ UPDATE status │
     │               │               │──────────────▶│
     │               │               │◀──────────────│
     │               │◀──────────────│               │
     │◀──────────────│               │               │
     │ Status:       │               │               │
     │ ACCEPTED      │               │               │
```

---

## 🔐 Authentication Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│Frontend │────▶│ Backend │────▶│Database │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │ Enter         │               │               │
     │ credentials   │               │               │
     │──────────────▶│               │               │
     │               │ POST /api/    │               │
     │               │ auth/login    │               │
     │               │──────────────▶│               │
     │               │               │ Verify        │
     │               │               │ password      │
     │               │               │──────────────▶│
     │               │               │◀──────────────│
     │               │               │ Generate JWT  │
     │               │◀──────────────│               │
     │               │ { token,      │               │
     │               │   role,       │               │
     │               │   user }      │               │
     │◀──────────────│               │               │
     │               │               │               │
     │               │ Store in      │               │
     │               │ localStorage: │               │
     │               │ - anc_token   │               │
     │               │ - anc_role    │               │
     │               │ - anc_user    │               │
     │               │               │               │
     │               │ Redirect to   │               │
     │               │ dashboard     │               │
     │◀──────────────│               │               │
     │               │               │               │
     │ All future    │               │               │
     │ requests      │               │               │
     │──────────────▶│               │               │
     │               │ Authorization:│               │
     │               │ Bearer <token>│               │
     │               │──────────────▶│               │
     │               │               │ Verify JWT    │
     │               │               │ Extract user  │
     │               │               │               │
```

---

## 🗂️ Database Schema

```
┌─────────────────┐
│  anc_workers    │
├─────────────────┤
│ id (UUID) PK    │
│ full_name       │
│ phone (unique)  │
│ email           │
│ password_hash   │
│ health_center   │
│ district        │
│ created_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│    patients     │
├─────────────────┤
│ id (UUID) PK    │
│ worker_id FK    │
│ full_name       │
│ phone           │
│ age             │
│ address         │
│ village         │
│ district        │
│ lmp_date        │
│ edd_date        │
│ blood_group     │
│ created_at      │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   anc_visits    │
├─────────────────┤
│ id (UUID) PK    │
│ patient_id FK   │
│ worker_id FK    │
│ structured_data │ (JSONB)
│ clinical_summary│
│ risk_level      │
│ risk_score      │
│ risk_factors    │ (JSONB)
│ recommendations │ (JSONB)
│ status          │
│ created_at      │
└─────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐
│ consultations   │
├─────────────────┤
│ id (UUID) PK    │
│ visit_id FK     │
│ patient_id FK   │
│ doctor_id FK    │
│ status          │
│ doctor_notes    │
│ diagnosis       │
│ action_plan     │
│ created_at      │
│ accepted_at     │
│ completed_at    │
└─────────────────┘
         │
         │ N:1
         ▼
┌─────────────────┐
│    doctors      │
├─────────────────┤
│ id (UUID) PK    │
│ full_name       │
│ phone (unique)  │
│ email           │
│ password_hash   │
│ specialization  │
│ hospital        │
│ district        │
│ registration_no │
│ is_available    │
│ created_at      │
└─────────────────┘
```

---

## 🌐 API Endpoints Map

```
Frontend (5173)
    │
    ├─ Public Routes
    │   ├─ / ──────────────────────────▶ Landing Page
    │   ├─ /worker/login ───────────────▶ Worker Login
    │   ├─ /worker/signup ──────────────▶ Worker Signup
    │   ├─ /doctor/login ───────────────▶ Doctor Login
    │   └─ /doctor/signup ──────────────▶ Doctor Signup
    │
    ├─ Worker Routes (Protected)
    │   ├─ /worker/dashboard ───────────▶ Dashboard
    │   ├─ /worker/patients ────────────▶ Patient List
    │   ├─ /worker/patients/new ────────▶ Create Patient
    │   ├─ /worker/patients/:id ────────▶ Patient Detail
    │   ├─ /worker/visits/new ──────────▶ Register Visit
    │   └─ /worker/visits/:id/result ───▶ Visit Result
    │
    └─ Doctor Routes (Protected)
        ├─ /doctor/dashboard ───────────▶ Dashboard
        ├─ /doctor/consultations ───────▶ Queue
        ├─ /doctor/consultations/:id ───▶ Detail
        └─ /doctor/history ─────────────▶ History

Backend (8080)
    │
    ├─ Worker Auth
    │   ├─ POST   /api/auth/signup
    │   ├─ POST   /api/auth/login
    │   └─ GET    /api/auth/me
    │
    ├─ Doctor Auth
    │   ├─ POST   /api/doctor/auth/signup
    │   ├─ POST   /api/doctor/auth/login
    │   └─ GET    /api/doctor/auth/me
    │
    ├─ Patients
    │   ├─ POST   /api/patients
    │   ├─ GET    /api/patients
    │   └─ GET    /api/patients/{id}
    │
    ├─ ANC Visits
    │   ├─ POST   /api/anc/register-visit
    │   ├─ GET    /api/anc/visits/{id}
    │   ├─ GET    /api/anc/patients/{id}/visits
    │   ├─ GET    /api/anc/visits/high-risk
    │   └─ GET    /api/anc/visits/critical
    │
    ├─ Consultations
    │   ├─ GET    /api/consultations/queue
    │   ├─ GET    /api/consultations/{id}
    │   ├─ POST   /api/consultations/{id}/accept
    │   ├─ POST   /api/consultations/{id}/start-call
    │   ├─ POST   /api/consultations/{id}/complete
    │   └─ GET    /api/consultations/my-history
    │
    └─ Documentation
        ├─ GET    /swagger-ui/index.html
        ├─ GET    /v3/api-docs
        └─ GET    /api-tester.html

RAG Pipeline (8000)
    │
    ├─ POST   /analyze-risk
    └─ GET    /health
```

---

## 🔒 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

Layer 1: Frontend
├─ Protected Routes (React Router)
├─ Role-based rendering (WORKER/DOCTOR)
├─ Token storage (localStorage)
└─ Auto-logout on 401

Layer 2: Backend (Spring Security)
├─ JWT Authentication Filter
├─ Role-based Authorization (@PreAuthorize)
├─ CORS Configuration (allow all origins)
├─ Password Hashing (BCrypt)
└─ Token Validation

Layer 3: Database
├─ Encrypted passwords (BCrypt)
├─ UUID primary keys
├─ Foreign key constraints
└─ Indexed queries
```

---

## 📊 Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND STACK                            │
├─────────────────────────────────────────────────────────────┤
│ Framework:     React 18.3.1 + TypeScript 5.8.3              │
│ Build Tool:    Vite 5.4.19                                  │
│ Routing:       React Router DOM 6.30.1                      │
│ State:         React Context + TanStack Query 5.83.0        │
│ Forms:         React Hook Form 7.61.1 + Zod 3.25.76         │
│ HTTP:          Axios 1.13.5                                 │
│ UI:            ShadCN UI + Tailwind CSS 3.4.17              │
│ Icons:         Lucide React 0.462.0                         │
│ Notifications: Sonner 1.7.4                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BACKEND STACK                             │
├─────────────────────────────────────────────────────────────┤
│ Framework:     Spring Boot 3.2.0                            │
│ Security:      Spring Security + JWT (jjwt 0.12.3)          │
│ Database:      PostgreSQL / H2                              │
│ ORM:           Spring Data JPA                              │
│ API Docs:      Springdoc OpenAPI 2.3.0                      │
│ Validation:    Jakarta Validation                           │
│ JSON:          Jackson                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    AI PIPELINE STACK                         │
├─────────────────────────────────────────────────────────────┤
│ Framework:     FastAPI                                      │
│ AI Model:      OpenAI GPT-4o-mini                           │
│ Embeddings:    text-embedding-3-small                       │
│ RAG:           Custom implementation                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                          │
└─────────────────────────────────────────────────────────────┘

Frontend (Vercel/Netlify)
    │
    │ HTTPS
    │
    ▼
CDN (Cloudflare)
    │
    │ HTTPS
    │
    ▼
Backend (AWS/Railway/Heroku)
    │
    ├─ Load Balancer
    ├─ Auto-scaling
    └─ Health checks
    │
    ▼
Database (AWS RDS/Supabase)
    │
    ├─ Automated backups
    ├─ Read replicas
    └─ Encryption at rest
    │
    ▼
AI Pipeline (AWS Lambda/Railway)
    │
    ├─ Serverless functions
    └─ OpenAI API
```

---

## 📈 Performance Considerations

```
Frontend Optimizations:
├─ Code splitting (React.lazy)
├─ Image optimization
├─ Caching (React Query)
├─ Lazy loading
└─ Bundle size optimization

Backend Optimizations:
├─ Database indexing
├─ Query optimization
├─ Connection pooling
├─ Caching (Redis - future)
└─ Async processing

AI Pipeline Optimizations:
├─ Request batching
├─ Response caching
├─ Rate limiting
└─ Timeout handling
```

---

This architecture provides a scalable, secure, and maintainable foundation for the NeoSure maternal health application! 🚀

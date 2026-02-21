# 🌸 NeoSure - AI-Powered Antenatal Care Platform

> Empowering maternal healthcare through intelligent risk assessment and telemedicine

[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

NeoSure is a comprehensive antenatal care platform designed to improve maternal healthcare outcomes in rural and underserved areas. The system combines AI-powered risk assessment, real-time telemedicine consultations, and intelligent patient monitoring to provide world-class prenatal care.

### Key Highlights

- 🤖 **AI Risk Assessment**: Machine learning models analyze patient data to identify high-risk pregnancies
- 👨‍⚕️ **Telemedicine**: WebRTC-based video consultations connecting patients with specialist doctors
- 📊 **Smart Dashboard**: Priority-based patient queue sorted by risk levels
- 🔒 **Secure**: JWT authentication with role-based access control
- 🎨 **Beautiful UI**: NeoSure-themed design with Cormorant Garamond and Jost fonts

## ✨ Features

### For ANC Workers
- ✅ Patient registration and management
- ✅ ANC visit recording with comprehensive health metrics
- ✅ AI-powered risk assessment (LOW, MODERATE, HIGH, CRITICAL)
- ✅ Request specialist consultations for high-risk cases
- ✅ Track patient history and visit records

### For Doctors
- ✅ Priority-based patient queue (sorted by risk level)
- ✅ Detailed patient reports with vitals and medical history
- ✅ One-click video consultations via WebRTC
- ✅ Real-time signaling for peer-to-peer connections
- ✅ Consultation notes and prescription management

### AI/ML Features
- ✅ Risk prediction using patient vitals and medical history
- ✅ Symptom analysis and pattern recognition
- ✅ Personalized recommendations based on risk factors
- ✅ Integration with FastAPI ML pipeline

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  React Frontend │◄───────►│  Spring Boot    │◄───────►│  FastAPI ML     │
│  (Port 5174)    │         │  Backend        │         │  Pipeline       │
│                 │         │  (Port 8080)    │         │  (Port 8000)    │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        │                           │                           │
        ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  WebRTC         │         │  H2 Database    │         │  ML Models      │
│  Signaling      │         │  (In-Memory)    │         │  (Scikit-learn) │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18.2 with Vite
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **WebRTC**: SockJS + STOMP.js
- **Icons**: Lucide React
- **Styling**: Custom CSS with NeoSure theme

### Backend
- **Framework**: Spring Boot 3.2
- **Security**: Spring Security + JWT
- **Database**: H2 (Development), PostgreSQL (Production ready)
- **WebSocket**: Spring WebSocket + STOMP
- **ORM**: Spring Data JPA
- **Build Tool**: Maven

### AI/ML Pipeline
- **Framework**: FastAPI
- **ML Libraries**: Scikit-learn, Pandas, NumPy
- **Models**: Risk classification, symptom analysis

## 🚀 Getting Started

### Prerequisites

- Java 17 or higher
- Node.js 18 or higher
- Maven 3.8+
- Python 3.9+ (for ML pipeline)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ayushmanCodes2004/NeoCare.git
cd NeoCare
```

2. **Start the Backend**
```bash
cd Backend
mvn clean install
mvn spring-boot:run
```
Backend will start on `http://localhost:8080`

3. **Start the Frontend** (in a new terminal)
```bash
cd Frontend/anc-frontend
npm install
npm run dev
```
Frontend will start on `http://localhost:5174`

4. **Start the ML Pipeline** (optional, in a new terminal)
```bash
cd "Medical RAG Pipeline"
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
ML API will start on `http://localhost:8000`

### Quick Test

1. **ANC Worker Portal**:
   - Navigate to `http://localhost:5174/signup`
   - Create an ANC worker account
   - Login and register patients

2. **Doctor Portal**:
   - Navigate to `http://localhost:5174/doctor/signup`
   - Create a doctor account
   - Login to see the priority-based patient queue

## 📁 Project Structure

```
NeoCare/
├── Backend/                          # Spring Boot backend
│   ├── src/main/java/com/anc/
│   │   ├── controller/              # REST API controllers
│   │   ├── service/                 # Business logic
│   │   ├── entity/                  # JPA entities
│   │   ├── repository/              # Data access layer
│   │   ├── security/                # JWT & authentication
│   │   ├── dto/                     # Data transfer objects
│   │   └── config/                  # Configuration classes
│   └── src/main/resources/
│       ├── application.yml          # App configuration
│       └── *.sql                    # Database schemas
│
├── Frontend/anc-frontend/           # React frontend
│   ├── src/
│   │   ├── pages/                   # Page components
│   │   ├── components/              # Reusable components
│   │   ├── context/                 # React context (auth)
│   │   ├── routes/                  # Route protection
│   │   ├── styles/                  # CSS stylesheets
│   │   ├── api/                     # API client functions
│   │   └── utils/                   # Utility functions
│   └── public/                      # Static assets
│
├── Medical RAG Pipeline/            # FastAPI ML service
│   ├── main.py                      # FastAPI app
│   ├── models/                      # ML models
│   └── requirements.txt             # Python dependencies
│
└── Documentation/                   # Project documentation
    ├── DOCTOR_DASHBOARD_COMPLETE_MAPPING.md
    ├── WEBRTC_IMPLEMENTATION_COMPLETE.md
    └── API_DOCUMENTATION.md
```

## 📚 API Documentation

### Authentication Endpoints

#### ANC Worker
- `POST /api/auth/signup` - Register new ANC worker
- `POST /api/auth/login` - Login ANC worker

#### Doctor
- `POST /api/auth/doctor/signup` - Register new doctor
- `POST /api/auth/doctor/login` - Login doctor
- `GET /api/auth/doctor/me` - Get doctor profile

### Patient Management
- `POST /api/patients` - Register new patient
- `GET /api/patients` - Get all patients for worker
- `GET /api/patients/{id}` - Get patient details

### ANC Visits
- `POST /api/anc/register-visit` - Record new ANC visit
- `GET /api/anc/visits/{visitId}` - Get visit details
- `GET /api/anc/patients/{patientId}/visits` - Get patient visit history
- `GET /api/anc/visits/high-risk` - Get high-risk visits
- `GET /api/anc/visits/critical` - Get critical visits

### Consultations
- `POST /api/consultations/request` - Request doctor consultation
- `GET /api/consultations/pending` - Get pending consultations (Doctor)
- `GET /api/consultations/my-consultations` - Get doctor's consultations
- `PUT /api/consultations/{id}/accept` - Accept consultation
- `PUT /api/consultations/{id}/start` - Start video consultation
- `PUT /api/consultations/{id}/complete` - Complete consultation

### WebRTC Signaling
- `WS /ws/consultation` - WebSocket endpoint for signaling
- `/app/signal/offer` - Send WebRTC offer
- `/app/signal/answer` - Send WebRTC answer
- `/app/signal/ice-candidate` - Exchange ICE candidates

For complete API documentation, see [DOCTOR_DASHBOARD_COMPLETE_MAPPING.md](DOCTOR_DASHBOARD_COMPLETE_MAPPING.md)

## 🎨 Design System

### Color Palette
- **Terra**: `#C4622D` / `#C06536` - Primary brand color
- **Peach**: `#F5E6D8` - Secondary accent
- **Cream**: `#FAF4EE` - Background tint

### Typography
- **Headings**: Cormorant Garamond (serif)
- **Body**: Jost (sans-serif)

### Risk Level Colors
- **Critical**: Red `#dc2626`
- **High**: Orange `#f59e0b`
- **Moderate**: Blue `#3b82f6`
- **Low**: Green `#10b981`

## 🖼️ Screenshots

### Landing Page
Beautiful NeoSure-themed landing page with Namaste greeting and feature highlights.

### ANC Worker Dashboard
Clean dashboard showing registered patients and recent activities.

### Doctor Dashboard
Priority-based patient queue with risk indicators and one-click video consultations.

### Video Consultation
WebRTC-powered video calls with real-time peer-to-peer connection.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Ayushman** - Full Stack Developer & AI/ML Engineer
- GitHub: [@ayushmanCodes2004](https://github.com/ayushmanCodes2004)

## 🙏 Acknowledgments

- Ministry of Health & Family Welfare, Government of India
- National Health Mission (NHM)
- All healthcare workers serving in rural areas

## 📞 Support

For support, email ayushman@example.com or open an issue in the repository.

---

Made with ❤️ for maternal healthcare in India 🇮🇳

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { DoctorAuthProvider } from './context/DoctorAuthContext';
import WorkerRoute from './routes/WorkerRoute';
import DoctorRoute from './routes/DoctorRoute';

// Import existing pages
import DoctorLoginPage from './pages/DoctorLoginPage';
import DoctorSignupPage from './pages/DoctorSignupPage';
import DoctorDashboardPage from './pages/DoctorDashboardPage';
import ConsultationListPage from './pages/ConsultationListPage';
import ConsultationDetailPage from './pages/ConsultationDetailPage';
import VideoConsultationPage from './pages/VideoConsultationPage';

import LandingPage from './pages/LandingPage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PatientListPage from './pages/PatientListPage';
import PatientCreatePage from './pages/PatientCreatePage';
import PatientDetailPage from './pages/PatientDetailPage';
import AncVisitFormPage from './pages/AncVisitFormPage';
import VisitResultPage from './pages/VisitResultPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <DoctorAuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Worker Portal */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/dashboard" element={<WorkerRoute />}>
              <Route index element={<DashboardPage />} />
            </Route>
            <Route path="/patients" element={<WorkerRoute />}>
              <Route index element={<PatientListPage />} />
              <Route path="new" element={<PatientCreatePage />} />
              <Route path=":id" element={<PatientDetailPage />} />
            </Route>
            <Route path="/visits" element={<WorkerRoute />}>
              <Route path="new/:patientId" element={<AncVisitFormPage />} />
              <Route path=":visitId" element={<VisitResultPage />} />
            </Route>

            {/* Doctor Portal */}
            <Route path="/doctor/login" element={<DoctorLoginPage />} />
            <Route path="/doctor/signup" element={<DoctorSignupPage />} />
            <Route path="/doctor" element={<DoctorRoute />}>
              <Route index element={<Navigate to="/doctor/dashboard" replace />} />
              <Route path="dashboard" element={<DoctorDashboardPage />} />
              <Route path="queue" element={<ConsultationListPage />} />
              <Route path="consultations/:id" element={<ConsultationDetailPage />} />
              <Route path="consultations/:id/video" element={<VideoConsultationPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </DoctorAuthProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

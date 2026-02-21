import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './routes/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import PatientListPage from './pages/PatientListPage';
import PatientCreatePage from './pages/PatientCreatePage';
import PatientDetailPage from './pages/PatientDetailPage';
import AncVisitFormPage from './pages/AncVisitFormPage';
import VisitResultPage from './pages/VisitResultPage';
import DoctorLoginPage from './pages/DoctorLoginPage';
import DoctorSignupPage from './pages/DoctorSignupPage';
import DoctorDashboardPage from './pages/DoctorDashboardPage';
import ConsultationListPage from './pages/ConsultationListPage';
import ConsultationDetailPage from './pages/ConsultationDetailPage';
import VideoConsultationPage from './pages/VideoConsultationPage';

/**
 * Main App component with routing
 */
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          {/* Doctor public routes */}
          <Route path="/doctor/login" element={<DoctorLoginPage />} />
          <Route path="/doctor/signup" element={<DoctorSignupPage />} />

          {/* Protected routes - ANC Worker */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              
              {/* Patient routes */}
              <Route path="/patients" element={<PatientListPage />} />
              <Route path="/patients/new" element={<PatientCreatePage />} />
              <Route path="/patients/:id" element={<PatientDetailPage />} />
              
              {/* Visit routes */}
              <Route path="/visits/new/:patientId" element={<AncVisitFormPage />} />
              <Route path="/visits/:id/result" element={<VisitResultPage />} />
              <Route path="/visits/:id" element={<VisitResultPage />} />
            </Route>
          </Route>

          {/* Protected routes - Doctor */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/doctor/dashboard" element={<DoctorDashboardPage />} />
              <Route path="/doctor/consultations" element={<ConsultationListPage />} />
              <Route path="/doctor/consultations/:id" element={<ConsultationDetailPage />} />
            </Route>
          </Route>

          {/* Video consultation - Full screen, no layout */}
          <Route element={<ProtectedRoute />}>
            <Route path="/doctor/video-consultation/:id" element={<VideoConsultationPage />} />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

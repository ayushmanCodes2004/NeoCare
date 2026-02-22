import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Landing from "./pages/Landing";
import NotFound from "./pages/NotFound";
import WorkerLogin from "./pages/worker/WorkerLogin";
import WorkerSignup from "./pages/worker/WorkerSignup";
import WorkerDashboard from "./pages/worker/WorkerDashboard";
import PatientList from "./pages/worker/PatientList";
import PatientCreate from "./pages/worker/PatientCreate";
import PatientDetail from "./pages/worker/PatientDetail";
import VisitForm from "./pages/worker/VisitForm";
import VisitResult from "./pages/worker/VisitResult";
import DoctorLogin from "./pages/doctor/DoctorLogin";
import DoctorSignup from "./pages/doctor/DoctorSignup";
import DoctorDashboard from "./pages/doctor/DoctorDashboard";
import ConsultationQueue from "./pages/doctor/ConsultationQueue";
import ConsultationDetail from "./pages/doctor/ConsultationDetail";
import DoctorHistory from "./pages/doctor/DoctorHistory";
import VideoConsultation from "./pages/doctor/VideoConsultation";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/worker/login" element={<WorkerLogin />} />
            <Route path="/worker/signup" element={<WorkerSignup />} />
            <Route path="/doctor/login" element={<DoctorLogin />} />
            <Route path="/doctor/signup" element={<DoctorSignup />} />
            <Route path="/worker/dashboard" element={<ProtectedRoute requiredRole="WORKER"><WorkerDashboard /></ProtectedRoute>} />
            <Route path="/worker/patients" element={<ProtectedRoute requiredRole="WORKER"><PatientList /></ProtectedRoute>} />
            <Route path="/worker/patients/new" element={<ProtectedRoute requiredRole="WORKER"><PatientCreate /></ProtectedRoute>} />
            <Route path="/worker/patients/:id" element={<ProtectedRoute requiredRole="WORKER"><PatientDetail /></ProtectedRoute>} />
            <Route path="/worker/visits/new" element={<ProtectedRoute requiredRole="WORKER"><VisitForm /></ProtectedRoute>} />
            <Route path="/worker/visits/:visitId/result" element={<ProtectedRoute requiredRole="WORKER"><VisitResult /></ProtectedRoute>} />
            <Route path="/doctor/dashboard" element={<ProtectedRoute requiredRole="DOCTOR"><DoctorDashboard /></ProtectedRoute>} />
            <Route path="/doctor/consultations" element={<ProtectedRoute requiredRole="DOCTOR"><ConsultationQueue /></ProtectedRoute>} />
            <Route path="/doctor/consultations/:id" element={<ProtectedRoute requiredRole="DOCTOR"><ConsultationDetail /></ProtectedRoute>} />
            <Route path="/doctor/consultations/:id/video" element={<ProtectedRoute requiredRole="DOCTOR"><VideoConsultation /></ProtectedRoute>} />
            <Route path="/doctor/history" element={<ProtectedRoute requiredRole="DOCTOR"><DoctorHistory /></ProtectedRoute>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;

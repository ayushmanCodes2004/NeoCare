import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

/**
 * Redirects to appropriate dashboard based on user role
 */
export default function RoleBasedRedirect() {
  const { userRole } = useAuth();

  if (userRole === 'DOCTOR') {
    return <Navigate to="/doctor/dashboard" replace />;
  }
  
  return <Navigate to="/dashboard" replace />;
}

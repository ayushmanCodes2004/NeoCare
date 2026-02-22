import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

const ProtectedRoute = ({ children, requiredRole }: { children: React.ReactNode; requiredRole?: string }) => {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (requiredRole && role !== requiredRole) return <Navigate to="/" replace />;

  return <>{children}</>;
};

export default ProtectedRoute;

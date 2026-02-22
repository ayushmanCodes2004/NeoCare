import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function WorkerRoute() {
  const { isAuth, ready } = useAuth();
  
  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-[3px] border-teal-500 border-t-transparent" />
      </div>
    );
  }
  
  return isAuth ? <Outlet /> : <Navigate to="/login" replace />;
}

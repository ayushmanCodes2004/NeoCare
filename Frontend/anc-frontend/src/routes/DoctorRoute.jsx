import { Navigate, Outlet } from 'react-router-dom';
import { useDoctorAuth } from '../hooks/useDoctorAuth';

export default function DoctorRoute() {
  const { isAuth, ready } = useDoctorAuth();
  
  if (!ready) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-[3px] border-teal-500 border-t-transparent" />
      </div>
    );
  }
  
  return isAuth ? <Outlet /> : <Navigate to="/doctor/login" replace />;
}

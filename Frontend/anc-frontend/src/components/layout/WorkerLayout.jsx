import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  LogOut, 
  User,
  Stethoscope 
} from 'lucide-react';
import { clsx } from 'clsx';

export default function WorkerLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/patients', icon: Users, label: 'Patients' },
    { path: '/visits', icon: Stethoscope, label: 'Visits' },
  ];

  return (
    <div className="min-h-screen bg-navy-950">
      {/* Top Navigation */}
      <nav className="glass border-b border-white/10 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/dashboard" className="font-display text-xl font-bold text-teal-400">
                ANC Portal
              </Link>
              <div className="hidden md:flex items-center gap-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname.startsWith(item.path);
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={clsx(
                        'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all',
                        isActive
                          ? 'bg-teal-500/20 text-teal-400'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                      )}
                    >
                      <Icon size={18} />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-slate-200">{user?.fullName}</p>
                <p className="text-xs text-slate-500">{user?.healthCenter}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-all"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}

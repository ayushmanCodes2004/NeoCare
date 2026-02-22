import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Heart, LogOut, Home, Users, ClipboardList, History } from 'lucide-react';

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isWorker = role === 'WORKER';
  const navItems = isWorker
    ? [
        { to: '/worker/dashboard', label: 'Dashboard', icon: Home },
        { to: '/worker/patients', label: 'Patients', icon: Users },
      ]
    : [
        { to: '/doctor/dashboard', label: 'Dashboard', icon: Home },
        { to: '/doctor/consultations', label: 'Queue', icon: ClipboardList },
        { to: '/doctor/history', label: 'History', icon: History },
      ];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 bg-card border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link to={isWorker ? '/worker/dashboard' : '/doctor/dashboard'} className="flex items-center gap-2">
            <Heart className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold text-foreground">NeoSure</span>
          </Link>
          <nav className="hidden sm:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname.startsWith(item.to)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:block">
              {user?.fullName}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default AppLayout;

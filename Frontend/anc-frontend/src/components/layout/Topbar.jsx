import { useAuth } from '../../hooks/useAuth';
import { Activity, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Topbar() {
  const { user, userRole, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="horizontal-topbar">
      <div className="topbar-container">
        {/* Logo / Brand */}
        <div className="brand-horizontal">
          <div className="brand-icon-horizontal">
            <Activity size={24} strokeWidth={2.5} />
          </div>
          <div className="brand-text-horizontal">
            <div className="brand-name-horizontal">NeoSure</div>
            <div className="brand-tagline-horizontal">
              {userRole === 'DOCTOR' ? 'DOCTOR PORTAL' : 'ANC INTELLIGENCE'}
            </div>
          </div>
        </div>

        {/* Right Side - User Profile & Logout */}
        <div className="topbar-right-horizontal">
          {user && (
            <>
              <div className="user-profile-horizontal">
                <div className="user-info-horizontal">
                  <div className="user-name-horizontal">
                    {userRole === 'DOCTOR' ? `Dr. ${user.fullName}` : user.fullName}
                  </div>
                  <div className="user-role-horizontal">
                    {userRole === 'DOCTOR' 
                      ? (user.hospital || 'Doctor') 
                      : (user.healthCenter || 'ANC Worker')
                    }
                  </div>
                </div>
                <div className="user-avatar-horizontal">
                  {user.fullName?.charAt(0) || 'U'}
                </div>
              </div>
              <button 
                className="logout-btn-horizontal"
                onClick={handleLogout}
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

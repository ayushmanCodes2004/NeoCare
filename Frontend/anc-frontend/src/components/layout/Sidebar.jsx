import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { LayoutDashboard, Users, UserPlus, Activity, Settings, LogOut, ChevronRight } from 'lucide-react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/patients', label: 'My Patients', icon: Users },
  { to: '/patients/new', label: 'New Patient', icon: UserPlus },
];

export default function Sidebar() {
  const { worker, logout } = useAuth();

  return (
    <aside className="sidebar">
      {/* Logo / Brand */}
      <div className="sidebar-header">
        <div className="brand">
          <div className="brand-icon">🌸</div>
          <div className="brand-text">
            <div className="brand-name">NeoSure</div>
            <div className="brand-tagline">ANC Care Portal</div>
          </div>
        </div>
      </div>

      {/* Worker Profile Card */}
      {worker && (
        <div className="worker-card">
          <div className="worker-avatar">
            <Activity size={24} />
          </div>
          <div className="worker-info">
            <div className="worker-name">{worker.fullName}</div>
            <div className="worker-location">
              <span className="location-icon">📍</span>
              {worker.healthCenter}
            </div>
            <div className="worker-district">{worker.district}</div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section">
          <div className="nav-label">Main Menu</div>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <Icon className="nav-icon" size={20} />
              <span className="nav-text">{label}</span>
              <ChevronRight className="nav-arrow" size={16} />
            </NavLink>
          ))}
        </div>

        <div className="nav-section">
          <div className="nav-label">Settings</div>
          <NavLink to="/profile" className="nav-item">
            <Settings className="nav-icon" size={20} />
            <span className="nav-text">Profile</span>
            <ChevronRight className="nav-arrow" size={16} />
          </NavLink>
        </div>
      </nav>

      {/* Logout Button */}
      <div className="sidebar-footer">
        <button onClick={logout} className="logout-btn">
          <LogOut size={20} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

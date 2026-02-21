import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getMyPatients } from '../api/patientApi';
import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import Spinner from '../components/ui/Spinner';
import '../styles/dashboard.css';

/**
 * Main Dashboard - Overview of ANC Worker's patients and activities
 * Redesigned with NeoSure professional theme
 */
export default function DashboardPage() {
  const navigate = useNavigate();
  const { userRole } = useAuth();
  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState([]);
  const [workerInfo, setWorkerInfo] = useState(null);

  // Redirect doctors to their dashboard
  useEffect(() => {
    if (userRole === 'DOCTOR') {
      navigate('/doctor/dashboard', { replace: true });
      return;
    }
  }, [userRole, navigate]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const patientsData = await getMyPatients();
        setPatients(patientsData);
        
        // Get worker info from localStorage
        const storedWorkerInfo = JSON.parse(localStorage.getItem('workerInfo') || '{}');
        setWorkerInfo(storedWorkerInfo);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="lg" />
        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Calculate statistics from real data
  const totalPatients = patients.length;
  const recentPatients = patients.slice(0, 5); // Show 5 most recent

  // Get today's date
  const today = new Date();
  const dateStr = today.toLocaleDateString('en-IN', { 
    weekday: 'long', 
    day: 'numeric', 
    month: 'long', 
    year: 'numeric' 
  });

  const getInitials = (name) => {
    if (!name) return 'P';
    const parts = name.split(' ');
    return parts.length > 1 ? parts[0][0] + parts[1][0] : parts[0][0];
  };



  return (
    <div className="neosure-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div>
          <p className="header-eyebrow">Supporting Mothers Across India</p>
          <h1 className="header-title">Namaste, {workerInfo?.fullName?.split(' ')[0] || 'Health Worker'}</h1>
          <p className="header-subtitle">
            Today is {dateStr}
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-secondary"
            onClick={() => navigate('/patients/new')}
          >
            Register New Patient
          </button>
          <button 
            className="btn-primary-alert"
            onClick={() => navigate('/patients')}
          >
            View All Patients
          </button>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card-new">
          <p className="stat-label">Total Registered Patients</p>
          <div className="stat-value-row">
            <span className="stat-value-large">{totalPatients}</span>
          </div>
        </div>

        <div className="stat-card-new">
          <p className="stat-label">Recent Patients</p>
          <div className="stat-value-row">
            <span className="stat-value-large stat-primary">{recentPatients.length}</span>
            <span className="stat-secondary">last registered</span>
          </div>
        </div>
      </div>

      {/* Recent Patients List */}
      <div className="card-white">
        <div className="card-header">
          <h2 className="card-title">Recent Patients</h2>
          <Link to="/patients" className="link-primary">View All Patients</Link>
        </div>

        {recentPatients.length === 0 ? (
          <div className="empty-state">
            <CheckCircle size={48} className="empty-icon" />
            <h3>No patients registered yet</h3>
            <p>Start by registering your first patient</p>
            <button 
              className="btn-primary-empty"
              onClick={() => navigate('/patients/new')}
            >
              Register New Patient
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Patient Details</th>
                  <th>Age</th>
                  <th>Phone</th>
                  <th>District</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {recentPatients.map((patient) => (
                  <tr key={patient.patientId} className="table-row-hover">
                    <td>
                      <div className="patient-cell">
                        <div className="patient-avatar">
                          {getInitials(patient.fullName)}
                        </div>
                        <div>
                          <p className="patient-name">{patient.fullName}</p>
                          <p className="patient-id">RCH ID: {patient.rchId || 'N/A'}</p>
                        </div>
                      </div>
                    </td>
                    <td className="text-sm">{patient.age} years</td>
                    <td className="text-sm">{patient.phone}</td>
                    <td className="text-sm">{patient.district}</td>
                    <td className="text-right">
                      <button 
                        className="btn-link"
                        onClick={() => navigate(`/patients/${patient.patientId}`)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

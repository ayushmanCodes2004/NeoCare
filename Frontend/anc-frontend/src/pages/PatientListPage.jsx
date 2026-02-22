import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getPatients } from '../api/patientApi';
import { Search, UserPlus, ShieldPlus, Users, AlertTriangle, Calendar, ChevronRight, Activity, TrendingUp, Clock, Filter } from 'lucide-react';
import { cn } from '../utils/cn';
import Spinner from '../components/ui/Spinner';
import '../styles/dashboard.css';

/**
 * Patient List Page - Same design as Dashboard
 */
export default function PatientListPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState('all');
  const [filterRisk, setFilterRisk] = useState('all');

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const data = await getPatients();
        setPatients(data);
      } catch (err) {
        console.error('Failed to fetch patients:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPatients();
  }, []);

  const filteredPatients = patients.filter(p => {
    const matchesSearch = 
      p.fullName?.toLowerCase().includes(search.toLowerCase()) ||
      p.rchId?.toLowerCase().includes(search.toLowerCase()) ||
      p.phone?.includes(search);
    
    const matchesRisk = filterRisk === 'all' || p.riskLevel === filterRisk;
    
    return matchesSearch && matchesRisk;
  });

  // Calculate stats
  const highRiskCount = patients.filter(p => 
    p.riskLevel === 'CRITICAL' || p.riskLevel === 'HIGH'
  ).length;

  const lowRiskCount = patients.filter(p => 
    p.riskLevel === 'LOW'
  ).length;

  const stats = [
    { 
      label: "Total Patients", 
      value: patients.length, 
      icon: Users, 
      color: 'primary', 
      badge: 'ACTIVE',
      trend: '+8%'
    },
    { 
      label: "High Risk", 
      value: highRiskCount, 
      icon: AlertTriangle, 
      color: 'warning', 
      badge: 'PRIORITY',
      trend: '-3%'
    },
    { 
      label: "Low Risk", 
      value: lowRiskCount, 
      icon: ShieldPlus, 
      color: 'success', 
      badge: 'SAFE',
      trend: '+12%'
    },
  ];

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="lg" />
        <p>Loading patients...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      {/* Stats Grid */}
      <div className="stats-container">
        {stats.map((stat, i) => (
          <div key={i} className={`stat-card stat-${stat.color}`}>
            <div className="stat-header">
              <div className="stat-icon-wrapper">
                <stat.icon className="stat-icon" size={24} />
              </div>
              <span className="stat-badge">{stat.badge}</span>
            </div>
            <div className="stat-body">
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
            <div className="stat-footer">
              <TrendingUp size={14} />
              <span className="stat-trend">{stat.trend} from last month</span>
            </div>
          </div>
        ))}
      </div>

      {/* Search & Filter Bar */}
      <div className="search-filter-section">
        <div className="search-wrapper">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, RCH ID, or phone number..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        
        <div className="filter-wrapper">
          <Filter size={18} />
          <select 
            className="filter-select"
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
          >
            <option value="all">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {/* Patient List Section */}
      <div className="patients-section">
        <div className="section-header">
          <div className="section-title-wrapper">
            <h2 className="section-title">All Patients</h2>
            <span className="patient-count">{filteredPatients.length} patients</span>
          </div>
          <div className="section-tabs">
            <button 
              className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              <Users size={16} />
              All Patients
            </button>
            <button 
              className={`tab-btn ${activeTab === 'recent' ? 'active' : ''}`}
              onClick={() => setActiveTab('recent')}
            >
              <Clock size={16} />
              Recent
            </button>
          </div>
        </div>

        {/* Patient Cards */}
        <div className="patient-grid">
          {filteredPatients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3 className="empty-title">
                {search || filterRisk !== 'all' ? 'No patients found' : 'No patients yet'}
              </h3>
              <p className="empty-text">
                {search || filterRisk !== 'all'
                  ? 'Try adjusting your search or filter' 
                  : 'Start by registering your first patient'}
              </p>
              {!search && filterRisk === 'all' && (
                <button 
                  className="btn-primary"
                  onClick={() => navigate('/patients/new')}
                >
                  <UserPlus size={20} />
                  Register First Patient
                </button>
              )}
            </div>
          ) : (
            filteredPatients.map((patient) => (
              <Link 
                to={`/patients/${patient.id}`} 
                key={patient.id}
                className="patient-card"
              >
                <div className="patient-card-header">
                  <div className={cn(
                    "patient-avatar",
                    patient.riskLevel === 'CRITICAL' ? 'avatar-critical' :
                    patient.riskLevel === 'HIGH' ? 'avatar-high' :
                    'avatar-low'
                  )}>
                    {patient.riskLevel === 'LOW' ? (
                      <ShieldPlus size={24} />
                    ) : (
                      <AlertTriangle size={24} />
                    )}
                    <div className={cn(
                      "risk-dot",
                      patient.riskLevel === 'CRITICAL' ? 'dot-critical' :
                      patient.riskLevel === 'HIGH' ? 'dot-high' :
                      'dot-low'
                    )} />
                  </div>
                  <div className="patient-info">
                    <h3 className="patient-name">{patient.fullName}</h3>
                    <p className="patient-rch">RCH: {patient.rchId || 'N/A'}</p>
                  </div>
                  <ChevronRight className="card-arrow" size={20} />
                </div>
                
                <div className="patient-card-body">
                  <div className="patient-detail">
                    <span className="detail-label">Age</span>
                    <span className="detail-value">{patient.age || 'N/A'} years</span>
                  </div>
                  <div className="patient-detail">
                    <span className="detail-label">District</span>
                    <span className="detail-value">{patient.district || 'N/A'}</span>
                  </div>
                  <div className="patient-detail">
                    <span className="detail-label">Phone</span>
                    <span className="detail-value">{patient.phone || 'N/A'}</span>
                  </div>
                </div>

                <div className="patient-card-footer">
                  <span className={cn(
                    "risk-badge",
                    patient.riskLevel === 'CRITICAL' ? 'badge-critical' :
                    patient.riskLevel === 'HIGH' ? 'badge-high' :
                    'badge-low'
                  )}>
                    {patient.riskLevel === 'CRITICAL' ? 'Critical Risk' :
                     patient.riskLevel === 'HIGH' ? 'High Risk' :
                     'Low Risk'}
                  </span>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>

      {/* Floating Action Button */}
      <button 
        className="fab"
        onClick={() => navigate('/patients/new')}
        aria-label="Register new patient"
      >
        <UserPlus size={24} />
        <span className="fab-text">New Patient</span>
      </button>
    </div>
  );
}

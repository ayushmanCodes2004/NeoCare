import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { AlertTriangle, Search, Filter, ArrowRight } from 'lucide-react';
import axios from 'axios';
import Spinner from '../components/ui/Spinner';
import '../styles/dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Consultation List Page - View all consultations with filtering
 */
export default function ConsultationListPage() {
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status');
  
  const [loading, setLoading] = useState(true);
  const [consultations, setConsultations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState(statusFilter || 'ALL');

  useEffect(() => {
    const fetchConsultations = async () => {
      try {
        const token = localStorage.getItem('anc_token');
        const response = await axios.get(`${API_BASE_URL}/api/consultations/my-history`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setConsultations(response.data);
      } catch (err) {
        console.error('Failed to fetch consultations:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchConsultations();
  }, []);

  const filteredConsultations = consultations.filter(c => {
    const matchesSearch = c.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         c.patientRchId.includes(searchTerm);
    const matchesStatus = filterStatus === 'ALL' || c.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL': return 'risk-critical';
      case 'HIGH': return 'risk-high';
      case 'MODERATE': return 'risk-moderate';
      default: return 'risk-low';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'PENDING': return 'status-pending';
      case 'SCHEDULED': return 'status-scheduled';
      case 'COMPLETED': return 'status-completed';
      case 'CANCELLED': return 'status-cancelled';
      default: return 'status-pending';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="lg" />
        <p>Loading consultations...</p>
      </div>
    );
  }

  return (
    <div className="doctor-dashboard">
      {/* Header */}
      <div className="welcome-section">
        <div className="welcome-content">
          <h1 className="welcome-title">Consultation Requests</h1>
          <p className="welcome-subtitle">
            Manage and respond to consultation requests
          </p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="section-container" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search 
              size={20} 
              style={{ 
                position: 'absolute', 
                left: '1rem', 
                top: '50%', 
                transform: 'translateY(-50%)',
                color: '#C4622D'
              }} 
            />
            <input
              type="text"
              placeholder="Search by patient name or RCH ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.875rem 1rem 0.875rem 3rem',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '1rem',
                fontFamily: 'Jost, sans-serif',
                transition: 'all 0.2s'
              }}
            />
          </div>
          
          <div style={{ position: 'relative', minWidth: '200px' }}>
            <Filter 
              size={20} 
              style={{ 
                position: 'absolute', 
                left: '1rem', 
                top: '50%', 
                transform: 'translateY(-50%)',
                color: '#C4622D'
              }} 
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                width: '100%',
                padding: '0.875rem 1rem 0.875rem 3rem',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '1rem',
                fontFamily: 'Jost, sans-serif',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              <option value="ALL">All Status</option>
              <option value="PENDING">Pending</option>
              <option value="SCHEDULED">Scheduled</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Results Count */}
        <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1rem' }}>
          Showing {filteredConsultations.length} consultation{filteredConsultations.length !== 1 ? 's' : ''}
        </p>

        {/* Consultations List */}
        {filteredConsultations.length === 0 ? (
          <div className="empty-state-simple">
            <AlertTriangle size={48} className="empty-icon" />
            <h3>No consultations found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <div className="consultations-list">
            {filteredConsultations.map((consultation) => (
              <Link
                key={consultation.consultationId}
                to={`/doctor/consultations/${consultation.consultationId}`}
                className="consultation-item"
              >
                <div className="consultation-risk">
                  <AlertTriangle className="risk-icon" size={24} />
                  <span className={`risk-badge ${getRiskBadgeClass(consultation.riskLevel)}`}>
                    {consultation.riskLevel}
                  </span>
                </div>
                
                <div className="consultation-info">
                  <h4 className="consultation-patient">{consultation.patientName}</h4>
                  <p className="consultation-meta">
                    RCH ID: {consultation.patientRchId} • {consultation.gestationWeeks}w {consultation.gestationDays}d
                  </p>
                  <p className="consultation-reason">{consultation.reasonForConsultation}</p>
                </div>

                <div className="consultation-status">
                  <span className={`status-badge ${getStatusBadgeClass(consultation.status)}`}>
                    {consultation.status}
                  </span>
                  {consultation.scheduledDateTime && (
                    <p className="consultation-time">
                      {new Date(consultation.scheduledDateTime).toLocaleString()}
                    </p>
                  )}
                </div>

                <ArrowRight className="consultation-arrow" size={20} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

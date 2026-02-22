import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AlertTriangle, Calendar, Video, FileText, User, Phone, MapPin, Clock } from 'lucide-react';
import axios from 'axios';
import Spinner from '../components/ui/Spinner';
import '../styles/dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Consultation Detail Page - View and manage a specific consultation
 */
export default function ConsultationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [consultation, setConsultation] = useState(null);
  const [scheduledDateTime, setScheduledDateTime] = useState('');
  const [notes, setNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchConsultation = async () => {
      try {
        const token = localStorage.getItem('anc_token');
        const response = await axios.get(`${API_BASE_URL}/api/consultations/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setConsultation(response.data);
        setNotes(response.data.doctorNotes || '');
      } catch (err) {
        console.error('Failed to fetch consultation:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchConsultation();
  }, [id]);

  const handleSchedule = async () => {
    if (!scheduledDateTime) {
      alert('Please select a date and time');
      return;
    }

    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      // TODO: Backend endpoint not implemented yet
      console.warn('Schedule endpoint not implemented on backend');
      await axios.post(
        `${API_BASE_URL}/api/consultations/${id}/schedule`,
        { scheduledDateTime },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Consultation scheduled successfully');
      window.location.reload();
    } catch (err) {
      alert('Failed to schedule consultation');
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!notes.trim()) {
      alert('Please add consultation notes before completing');
      return;
    }

    setActionLoading(true);
    try {
      const token = localStorage.getItem('anc_token');
      await axios.post(
        `${API_BASE_URL}/api/consultations/${id}/complete`,
        { doctorNotes: notes },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Consultation marked as completed');
      window.location.reload();
    } catch (err) {
      alert('Failed to complete consultation');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartVideo = () => {
    navigate(`/doctor/video-consultation/${id}`);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="lg" />
        <p>Loading consultation details...</p>
      </div>
    );
  }

  if (!consultation) {
    return (
      <div className="dashboard-loading">
        <p>Consultation not found</p>
      </div>
    );
  }

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

  return (
    <div className="doctor-dashboard">
      {/* Header */}
      <div className="welcome-section">
        <div className="welcome-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <h1 className="welcome-title">{consultation.patientName}</h1>
            <span className={`risk-badge ${getRiskBadgeClass(consultation.riskLevel)}`}>
              {consultation.riskLevel} RISK
            </span>
            <span className={`status-badge ${getStatusBadgeClass(consultation.status)}`}>
              {consultation.status}
            </span>
          </div>
          <p className="welcome-subtitle">
            RCH ID: {consultation.patientRchId} • {consultation.gestationWeeks}w {consultation.gestationDays}d
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        {/* Left Column - Patient & Consultation Info */}
        <div>
          {/* Patient Information */}
          <div className="section-container" style={{ marginBottom: '2rem' }}>
            <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>
              <User size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Patient Information
            </h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Full Name</p>
                <p style={{ fontSize: '1rem', fontWeight: 600 }}>{consultation.patientName}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Age</p>
                <p style={{ fontSize: '1rem', fontWeight: 600 }}>{consultation.patientAge} years</p>
              </div>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Phone</p>
                <p style={{ fontSize: '1rem', fontWeight: 600 }}>
                  <Phone size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                  {consultation.patientPhone}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Location</p>
                <p style={{ fontSize: '1rem', fontWeight: 600 }}>
                  <MapPin size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                  {consultation.patientDistrict}
                </p>
              </div>
            </div>
          </div>

          {/* Consultation Details */}
          <div className="section-container">
            <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>
              <FileText size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Consultation Details
            </h2>
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Reason for Consultation</p>
                <p style={{ fontSize: '1rem', lineHeight: 1.6 }}>{consultation.reasonForConsultation}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Requested By</p>
                <p style={{ fontSize: '1rem', fontWeight: 600 }}>{consultation.requestedByWorkerName}</p>
              </div>
              <div>
                <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Request Date</p>
                <p style={{ fontSize: '1rem' }}>
                  {new Date(consultation.requestedAt).toLocaleString()}
                </p>
              </div>
              {consultation.scheduledDateTime && (
                <div>
                  <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Scheduled For</p>
                  <p style={{ fontSize: '1rem', fontWeight: 600, color: '#C4622D' }}>
                    <Calendar size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                    {new Date(consultation.scheduledDateTime).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Actions & Notes */}
        <div>
          {/* Actions */}
          {consultation.status === 'PENDING' && (
            <div className="section-container" style={{ marginBottom: '2rem' }}>
              <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>
                <Calendar size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                Schedule Consultation
              </h2>
              <div style={{ display: 'grid', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                    Select Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    value={scheduledDateTime}
                    onChange={(e) => setScheduledDateTime(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '1rem'
                    }}
                  />
                </div>
                <button
                  onClick={handleSchedule}
                  disabled={actionLoading}
                  style={{
                    padding: '0.875rem 1.5rem',
                    background: '#C4622D',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {actionLoading ? 'Scheduling...' : 'Schedule Consultation'}
                </button>
              </div>
            </div>
          )}

          {consultation.status === 'SCHEDULED' && (
            <div className="section-container" style={{ marginBottom: '2rem' }}>
              <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>
                <Video size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
                Video Consultation
              </h2>
              <button
                onClick={handleStartVideo}
                style={{
                  width: '100%',
                  padding: '1rem 1.5rem',
                  background: 'linear-gradient(135deg, #C4622D 0%, #A0501F 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1.125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem'
                }}
              >
                <Video size={20} />
                Start Video Call
              </button>
            </div>
          )}

          {/* Doctor Notes */}
          <div className="section-container">
            <h2 className="section-title" style={{ marginBottom: '1.5rem' }}>
              <FileText size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Doctor's Notes
            </h2>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add your consultation notes, recommendations, and follow-up instructions..."
              disabled={consultation.status === 'COMPLETED'}
              style={{
                width: '100%',
                minHeight: '200px',
                padding: '1rem',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '1rem',
                fontFamily: 'Jost, sans-serif',
                resize: 'vertical',
                marginBottom: '1rem'
              }}
            />
            {consultation.status !== 'COMPLETED' && (
              <button
                onClick={handleComplete}
                disabled={actionLoading}
                style={{
                  width: '100%',
                  padding: '0.875rem 1.5rem',
                  background: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {actionLoading ? 'Completing...' : 'Mark as Completed'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

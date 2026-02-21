import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Video, Clock, FileText, ChevronRight, Activity } from 'lucide-react';
import axios from 'axios';
import Spinner from '../components/ui/Spinner';
import '../styles/dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Doctor Dashboard - Shows patients by risk priority with consultation actions
 */
export default function DoctorDashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [consultations, setConsultations] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientReport, setPatientReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [doctorInfo, setDoctorInfo] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const storedDoctorInfo = JSON.parse(localStorage.getItem('doctorInfo') || '{}');
      setDoctorInfo(storedDoctorInfo);

      // Fetch pending consultations (sorted by risk)
      const response = await axios.get(`${API_BASE_URL}/api/consultations/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Sort by risk priority: CRITICAL > HIGH > MODERATE > LOW
      const riskOrder = { CRITICAL: 0, HIGH: 1, MODERATE: 2, LOW: 3 };
      const sorted = response.data.sort((a, b) => 
        riskOrder[a.riskLevel] - riskOrder[b.riskLevel]
      );
      
      setConsultations(sorted);
    } catch (err) {
      console.error('Failed to fetch consultations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPatientReport = async (patientId, visitId) => {
    setLoadingReport(true);
    try {
      const token = localStorage.getItem('token');
      
      // Fetch visit details with full report
      const response = await axios.get(`${API_BASE_URL}/api/anc/visits/${visitId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPatientReport(response.data);
    } catch (err) {
      console.error('Failed to fetch patient report:', err);
      setPatientReport(null);
    } finally {
      setLoadingReport(false);
    }
  };

  const handleViewReport = (consultation) => {
    setSelectedPatient(consultation);
    fetchPatientReport(consultation.patientId, consultation.visitId);
  };

  const handleStartConsultation = async (consultationId) => {
    try {
      const token = localStorage.getItem('token');
      
      // Accept consultation first
      await axios.put(
        `${API_BASE_URL}/api/consultations/${consultationId}/accept`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Navigate to video consultation
      navigate(`/doctor/video-consultation/${consultationId}`);
    } catch (err) {
      console.error('Failed to start consultation:', err);
      alert('Failed to start consultation. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Spinner size="lg" />
        <p>Loading dashboard...</p>
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

  const getRiskIcon = (riskLevel) => {
    return riskLevel === 'CRITICAL' || riskLevel === 'HIGH' ? '🚨' : '⚠️';
  };

  // Calculate stats
  const criticalCount = consultations.filter(c => c.riskLevel === 'CRITICAL').length;
  const highCount = consultations.filter(c => c.riskLevel === 'HIGH').length;
  const totalPending = consultations.length;

  return (
    <div className="doctor-dashboard-new">
      {/* Welcome Header */}
      <div className="doctor-welcome-header">
        <div className="welcome-content">
          <h1 className="doctor-welcome-title">
            Namaste, Dr. {doctorInfo?.fullName?.split(' ').pop() || 'Doctor'} 🙏
          </h1>
          <p className="doctor-welcome-subtitle">
            {doctorInfo?.specialization} • {doctorInfo?.hospital}
          </p>
        </div>
        <div className="doctor-date">
          {new Date().toLocaleDateString('en-IN', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Priority Stats */}
      <div className="priority-stats">
        <div className="priority-card critical">
          <div className="priority-icon">🚨</div>
          <div className="priority-info">
            <div className="priority-count">{criticalCount}</div>
            <div className="priority-label">Critical Cases</div>
          </div>
        </div>
        <div className="priority-card high">
          <div className="priority-icon">⚠️</div>
          <div className="priority-info">
            <div className="priority-count">{highCount}</div>
            <div className="priority-label">High Risk</div>
          </div>
        </div>
        <div className="priority-card total">
          <div className="priority-icon">📋</div>
          <div className="priority-info">
            <div className="priority-count">{totalPending}</div>
            <div className="priority-label">Total Pending</div>
          </div>
        </div>
      </div>

      <div className="doctor-main-content">
        {/* Patient Queue */}
        <div className="patient-queue-section">
          <div className="section-header-doctor">
            <h2 className="section-title-doctor">
              <Activity size={24} />
              Patient Queue by Priority
            </h2>
          </div>

          {consultations.length === 0 ? (
            <div className="empty-state-doctor">
              <Clock size={64} className="empty-icon" />
              <h3>No Pending Consultations</h3>
              <p>All consultation requests will appear here sorted by risk priority</p>
            </div>
          ) : (
            <div className="patient-queue-list">
              {consultations.map((consultation) => (
                <div
                  key={consultation.consultationId}
                  className={`patient-queue-card ${getRiskBadgeClass(consultation.riskLevel)}`}
                >
                  <div className="queue-card-header">
                    <div className="patient-risk-badge">
                      <span className="risk-emoji">{getRiskIcon(consultation.riskLevel)}</span>
                      <span className={`risk-label ${getRiskBadgeClass(consultation.riskLevel)}`}>
                        {consultation.riskLevel}
                      </span>
                    </div>
                    <div className="queue-time">
                      <Clock size={14} />
                      {new Date(consultation.createdAt).toLocaleTimeString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>

                  <div className="queue-card-body">
                    <h3 className="patient-name-doctor">{consultation.patientName}</h3>
                    <div className="patient-meta-doctor">
                      <span>RCH ID: {consultation.patientRchId}</span>
                      <span>•</span>
                      <span>{consultation.gestationWeeks}w {consultation.gestationDays}d</span>
                      <span>•</span>
                      <span>Age: {consultation.patientAge}</span>
                    </div>
                    <p className="consultation-reason-doctor">
                      <strong>Reason:</strong> {consultation.reasonForConsultation}
                    </p>
                  </div>

                  <div className="queue-card-actions">
                    <button
                      className="btn-view-report"
                      onClick={() => handleViewReport(consultation)}
                    >
                      <FileText size={18} />
                      View Report
                    </button>
                    <button
                      className="btn-start-consultation"
                      onClick={() => handleStartConsultation(consultation.consultationId)}
                    >
                      <Video size={18} />
                      Start Video Call
                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Patient Report Panel */}
        {selectedPatient && (
          <div className="patient-report-panel">
            <div className="report-panel-header">
              <h3 className="report-panel-title">
                <FileText size={20} />
                Patient Report
              </h3>
              <button 
                className="close-panel-btn"
                onClick={() => {
                  setSelectedPatient(null);
                  setPatientReport(null);
                }}
              >
                ×
              </button>
            </div>

            {loadingReport ? (
              <div className="report-loading">
                <Spinner size="md" />
                <p>Loading report...</p>
              </div>
            ) : patientReport ? (
              <div className="report-content">
                <div className="report-section">
                  <h4>Patient Information</h4>
                  <div className="report-grid">
                    <div className="report-item">
                      <span className="report-label">Name:</span>
                      <span className="report-value">{selectedPatient.patientName}</span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">Age:</span>
                      <span className="report-value">{selectedPatient.patientAge} years</span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">RCH ID:</span>
                      <span className="report-value">{selectedPatient.patientRchId}</span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">Gestation:</span>
                      <span className="report-value">
                        {selectedPatient.gestationWeeks}w {selectedPatient.gestationDays}d
                      </span>
                    </div>
                  </div>
                </div>

                <div className="report-section">
                  <h4>Vitals</h4>
                  <div className="report-grid">
                    <div className="report-item">
                      <span className="report-label">BP:</span>
                      <span className="report-value">
                        {patientReport.systolicBp}/{patientReport.diastolicBp} mmHg
                      </span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">Weight:</span>
                      <span className="report-value">{patientReport.weight} kg</span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">Hemoglobin:</span>
                      <span className="report-value">{patientReport.hemoglobin} g/dL</span>
                    </div>
                    <div className="report-item">
                      <span className="report-label">Blood Sugar:</span>
                      <span className="report-value">{patientReport.bloodSugar} mg/dL</span>
                    </div>
                  </div>
                </div>

                {patientReport.symptoms && patientReport.symptoms.length > 0 && (
                  <div className="report-section">
                    <h4>Current Symptoms</h4>
                    <div className="symptoms-list">
                      {patientReport.symptoms.map((symptom, idx) => (
                        <span key={idx} className="symptom-tag">{symptom}</span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="report-section">
                  <h4>Risk Assessment</h4>
                  <div className={`risk-assessment-box ${getRiskBadgeClass(patientReport.riskLevel)}`}>
                    <div className="risk-level-large">
                      {getRiskIcon(patientReport.riskLevel)} {patientReport.riskLevel}
                    </div>
                    {patientReport.riskFactors && patientReport.riskFactors.length > 0 && (
                      <div className="risk-factors">
                        <strong>Risk Factors:</strong>
                        <ul>
                          {patientReport.riskFactors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {patientReport.recommendations && (
                  <div className="report-section">
                    <h4>AI Recommendations</h4>
                    <div className="recommendations-box">
                      {patientReport.recommendations}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="report-error">
                <p>Failed to load patient report</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

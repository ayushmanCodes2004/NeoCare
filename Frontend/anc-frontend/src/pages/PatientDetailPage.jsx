import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getPatient } from '../api/patientApi';
import { getPatientVisits } from '../api/visitApi';
import Spinner from '../components/ui/Spinner';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ErrorAlert from '../components/ui/ErrorAlert';
import { format } from 'date-fns';

/**
 * Patient detail page — shows patient info and visit history
 */
export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patientData, visitsData] = await Promise.all([
          getPatient(id),
          getPatientVisits(id),
        ]);
        setPatient(patientData);
        setVisits(visitsData);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load patient details');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div>
        <ErrorAlert message={error || 'Patient not found'} />
        <Button onClick={() => navigate('/patients')}>Back to Patients</Button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{patient.fullName}</h1>
          <p className="text-gray-600 mt-1">Patient ID: {patient.patientId}</p>
        </div>
        <Link to={`/visits/new/${patient.patientId}`}>
          <Button>
            <span>📋</span>
            New ANC Visit
          </Button>
        </Link>
      </div>

      {/* Patient Info Card */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Patient Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Phone</p>
            <p className="font-medium text-gray-900">{patient.phone}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Age</p>
            <p className="font-medium text-gray-900">{patient.age} years</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Address</p>
            <p className="font-medium text-gray-900">{patient.address}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Village</p>
            <p className="font-medium text-gray-900">{patient.village}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">District</p>
            <p className="font-medium text-gray-900">{patient.district}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Blood Group</p>
            <p className="font-medium text-gray-900">{patient.bloodGroup || 'Not specified'}</p>
          </div>
        </div>
      </div>

      {/* Pregnancy Details Card */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pregnancy Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">LMP Date</p>
            <p className="font-medium text-gray-900">
              {patient.lmpDate ? format(new Date(patient.lmpDate), 'dd MMM yyyy') : 'Not specified'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">EDD</p>
            <p className="font-medium text-gray-900">
              {patient.eddDate ? format(new Date(patient.eddDate), 'dd MMM yyyy') : 'Not specified'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Registered On</p>
            <p className="font-medium text-gray-900">
              {patient.createdAt ? format(new Date(patient.createdAt), 'dd MMM yyyy') : 'Unknown'}
            </p>
          </div>
        </div>
      </div>

      {/* Visit History */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Visit History ({visits.length})
        </h2>
        
        {visits.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-3">📋</div>
            <p className="text-gray-600 mb-4">No ANC visits recorded yet</p>
            <Link to={`/visits/new/${patient.patientId}`}>
              <Button>Record First Visit</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {visits.map((visit) => (
              <div
                key={visit.visitId}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-colors"
                onClick={() => navigate(`/visits/${visit.visitId}`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <Badge riskLevel={visit.riskLevel} />
                      <span className="text-sm text-gray-600">
                        {visit.createdAt ? format(new Date(visit.createdAt), 'dd MMM yyyy, HH:mm') : 'Unknown date'}
                      </span>
                    </div>
                    {visit.detectedRisks && visit.detectedRisks.length > 0 && (
                      <p className="text-sm text-gray-600 mt-2">
                        {visit.detectedRisks.length} risk factor{visit.detectedRisks.length !== 1 ? 's' : ''} detected
                      </p>
                    )}
                  </div>
                  <span className="text-blue-500 text-sm font-medium">View →</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

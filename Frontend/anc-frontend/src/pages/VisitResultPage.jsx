import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getVisit } from '../api/visitApi';
import RiskBanner from '../components/visits/RiskBanner';
import DetectedRisksList from '../components/visits/DetectedRisksList';
import Spinner from '../components/ui/Spinner';
import Button from '../components/ui/Button';
import ErrorAlert from '../components/ui/ErrorAlert';
import { format } from 'date-fns';

/**
 * Visit result page — displays risk assessment from FastAPI
 */
export default function VisitResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [visit, setVisit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVisit = async () => {
      try {
        const data = await getVisit(id);
        setVisit(data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load visit details');
      } finally {
        setLoading(false);
      }
    };
    fetchVisit();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !visit) {
    return (
      <div>
        <ErrorAlert message={error || 'Visit not found'} />
        <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
      </div>
    );
  }

  const riskAssessment = visit.riskAssessment || visit;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">ANC Visit Result</h1>
        <p className="text-gray-600 mt-1">
          Visit Date: {visit.createdAt ? format(new Date(visit.createdAt), 'dd MMM yyyy, HH:mm') : 'Unknown'}
        </p>
      </div>

      {/* Risk Banner */}
      <RiskBanner
        isHighRisk={riskAssessment.isHighRisk}
        riskLevel={riskAssessment.riskLevel}
        recommendation={riskAssessment.recommendation}
      />

      {/* Detected Risks */}
      {riskAssessment.detectedRisks && riskAssessment.detectedRisks.length > 0 && (
        <DetectedRisksList risks={riskAssessment.detectedRisks} />
      )}

      {/* Explanation */}
      {riskAssessment.explanation && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
          <h3 className="font-semibold text-gray-800 mb-3">Clinical Assessment</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{riskAssessment.explanation}</p>
        </div>
      )}

      {/* Patient Info */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 mb-4">
        <h3 className="font-semibold text-gray-800 mb-3">Patient Information</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {riskAssessment.patientName && (
            <div>
              <p className="text-gray-600">Patient</p>
              <p className="font-medium text-gray-900">{riskAssessment.patientName}</p>
            </div>
          )}
          {riskAssessment.age && (
            <div>
              <p className="text-gray-600">Age</p>
              <p className="font-medium text-gray-900">{riskAssessment.age} years</p>
            </div>
          )}
          {riskAssessment.gestationalWeeks && (
            <div>
              <p className="text-gray-600">Gestational Age</p>
              <p className="font-medium text-gray-900">{riskAssessment.gestationalWeeks} weeks</p>
            </div>
          )}
          {riskAssessment.confidence !== undefined && (
            <div>
              <p className="text-gray-600">Confidence</p>
              <p className="font-medium text-gray-900">{(riskAssessment.confidence * 100).toFixed(0)}%</p>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="secondary"
          onClick={() => navigate(`/patients/${visit.patientId}`)}
        >
          View Patient
        </Button>
        <Button
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </Button>
      </div>
    </div>
  );
}

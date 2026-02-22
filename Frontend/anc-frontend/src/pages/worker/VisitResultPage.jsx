import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { getVisit } from '../../api/visitApi';
import RiskReport from '../../components/visits/RiskReport';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import { ArrowLeft, Printer, Stethoscope } from 'lucide-react';
import { format } from 'date-fns';

export default function VisitResultPage() {
  const { visitId } = useParams();
  const { state }   = useLocation();
  const navigate    = useNavigate();
  const [visit, setVisit]   = useState(state || null);
  const [loading, setLoading] = useState(!state);

  useEffect(() => {
    if (!state) {
      getVisit(visitId).then(d => setVisit(d)).finally(() => setLoading(false));
    }
  }, [visitId, state]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!visit)  return <div className="p-8 text-slate-400">Visit not found.</div>;

  const risk = visit.riskAssessment;

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate(-1)}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-teal-400 mb-2 transition-colors">
            <ArrowLeft size={14} /> Back
          </button>
          <p className="section-label">Visit Result</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Risk Assessment</h1>
          <p className="text-xs text-slate-500 font-mono mt-0.5">
            {visit.savedAt && format(new Date(visit.savedAt), 'dd MMM yyyy, HH:mm')}
            {' · '}
            <span className={`${visit.status === 'AI_ANALYZED' ? 'text-teal-400' : visit.status === 'AI_FAILED' ? 'text-risk-high' : 'text-slate-400'}`}>
              {visit.status}
            </span>
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => window.print()}>
            <Printer size={15} />
          </Button>
          {visit.patientId && (
            <Button variant="secondary" size="sm" onClick={() => navigate(`/patients/${visit.patientId}`)}>
              <Stethoscope size={15} /> Patient
            </Button>
          )}
        </div>
      </div>

      {risk ? (
        <RiskReport risk={risk} />
      ) : (
        <div className="glass-card p-8 text-center text-slate-400">
          <p>Risk assessment not available for this visit.</p>
          {visit.message && <p className="text-sm mt-2 text-slate-500">{visit.message}</p>}
        </div>
      )}

      {risk?.isHighRisk && (
        <div className="mt-4 glass-card p-4 border-indigo-500/30 bg-indigo-500/5">
          <div className="flex items-center gap-2 mb-1">
            <Stethoscope size={16} className="text-indigo-400" />
            <p className="text-sm font-semibold text-indigo-300">Doctor Consultation Requested</p>
          </div>
          <p className="text-xs text-slate-400">
            A consultation has been automatically created in the doctor queue. Check the patient's profile for updates.
          </p>
          <Button variant="outline" size="sm" className="mt-3 border-indigo-500/40 text-indigo-400"
            onClick={() => navigate(`/patients/${visit.patientId}`)}>
            View Consultation Status →
          </Button>
        </div>
      )}
    </div>
  );
}

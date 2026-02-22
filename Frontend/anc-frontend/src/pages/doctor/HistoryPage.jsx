import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory } from '../../api/consultationApi';
import { useApi } from '../../hooks/useApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Spinner from '../../components/ui/Spinner';
import EmptyState from '../../components/ui/EmptyState';
import { ChevronRight, CheckCircle } from 'lucide-react';
import { format } from 'date-fns';

export default function HistoryPage() {
  const navigate = useNavigate();
  const { data: history, loading, run } = useApi(getHistory);
  useEffect(() => { run(); }, []);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-6">
        <p className="section-label text-indigo-400">Consultation History</p>
        <h1 className="font-display text-2xl font-bold text-slate-100">Past Consultations</h1>
        <p className="text-slate-400 text-sm">{history?.length || 0} total</p>
      </div>

      {!history?.length ? (
        <EmptyState icon="📂" title="No consultations yet" sub="Completed consultations will appear here." />
      ) : (
        <div className="space-y-2">
          {history.map(c => (
            <button key={c.consultationId}
              onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}
              className="w-full glass-card p-4 flex items-center justify-between hover:border-indigo-500/30 transition-all group text-left">
              <div className="flex items-center gap-4">
                <div className={`h-9 w-9 rounded-xl flex items-center justify-center flex-shrink-0
                  ${c.status === 'COMPLETED' ? 'bg-teal-500/20' : 'bg-white/5'}`}>
                  <CheckCircle size={18} className={c.status === 'COMPLETED' ? 'text-teal-400' : 'text-slate-600'} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <RiskBadge level={c.riskLevel} />
                    <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                      ${c.status === 'COMPLETED' ? 'text-teal-400 bg-teal-400/10' : 'text-slate-400 bg-white/5'}`}>
                      {c.status}
                    </span>
                  </div>
                  <p className="font-medium text-slate-200">{c.patientName || 'Patient'}</p>
                  <p className="text-xs text-slate-500">
                    {[c.patientAge && `Age ${c.patientAge}`, c.gestationalWeeks && `${c.gestationalWeeks}w`, c.district].filter(Boolean).join(' · ')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                {c.completedAt && (
                  <span className="text-xs text-slate-600">
                    {format(new Date(c.completedAt), 'dd MMM yyyy')}
                  </span>
                )}
                <ChevronRight size={16} className="text-slate-600 group-hover:text-indigo-400 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

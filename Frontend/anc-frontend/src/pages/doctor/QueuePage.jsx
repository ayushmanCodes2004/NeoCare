import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getQueue, acceptConsult } from '../../api/consultationApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Button from '../../components/ui/Button';
import Spinner from '../../components/ui/Spinner';
import Toast from '../../components/ui/Toast';
import EmptyState from '../../components/ui/EmptyState';
import { RefreshCw, ChevronRight, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

function QueueSection({ title, color, items, onAccept, accepting, navigate }) {
  if (items.length === 0) return null;
  const border = { critical: 'border-l-risk-critical', high: 'border-l-risk-high', medium: 'border-l-risk-medium' };
  const text   = { critical: 'text-risk-critical', high: 'text-risk-high', medium: 'text-risk-medium' };
  return (
    <div className="mb-6">
      <p className={`text-xs font-mono font-bold uppercase tracking-widest mb-3 ${text[color]}`}>
        {title} · {items.length}
      </p>
      <div className="space-y-2">
        {items.map(c => (
          <div key={c.consultationId}
            className={`glass-card p-4 border-l-4 ${border[color]} hover:bg-white/[0.02] transition-colors`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                  <RiskBadge level={c.riskLevel} />
                  <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                    ${c.status === 'ACCEPTED'    ? 'text-indigo-400 bg-indigo-400/10'
                    : c.status === 'IN_PROGRESS' ? 'text-teal-400 bg-teal-400/10 animate-pulse'
                    : 'text-slate-400 bg-white/5'}`}>
                    {c.status}
                  </span>
                  <span className="text-xs text-slate-600">
                    {c.createdAt && formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                  </span>
                </div>
                <p className="font-semibold text-slate-100">{c.patientName || 'Patient'}</p>
                <p className="text-sm text-slate-400">
                  {[c.patientAge && `Age ${c.patientAge}`, c.gestationalWeeks && `${c.gestationalWeeks}w GA`, c.district].filter(Boolean).join(' · ')}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">
                  ANC Worker: {c.workerName} · {c.healthCenter}
                </p>
                {c.detectedRisks?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {c.detectedRisks.slice(0, 3).map((r, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20">
                        {r}
                      </span>
                    ))}
                    {c.detectedRisks.length > 3 && (
                      <span className="text-[10px] text-slate-500">+{c.detectedRisks.length - 3} more</span>
                    )}
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-2 flex-shrink-0">
                {c.status === 'PENDING' && (
                  <Button size="sm" loading={accepting === c.consultationId}
                    className="bg-indigo-500 hover:bg-indigo-400 text-white"
                    onClick={() => onAccept(c.consultationId)}>
                    Accept
                  </Button>
                )}
                <Button size="sm" variant="secondary"
                  onClick={() => navigate(`/doctor/consultations/${c.consultationId}`)}>
                  Open <ChevronRight size={14} />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function QueuePage() {
  const navigate  = useNavigate();
  const [queue,     setQueue]     = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [accepting, setAccepting] = useState(null);
  const [toast,     setToast]     = useState(null);

  const fetch = useCallback(() => {
    return getQueue().then(setQueue).finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetch(); }, [fetch]);
  useEffect(() => {
    const t = setInterval(fetch, 30000);
    return () => clearInterval(t);
  }, [fetch]);

  const handleAccept = async (id) => {
    setAccepting(id);
    try {
      await acceptConsult(id);
      await fetch();
      setToast({ msg: 'Case accepted successfully', type: 'success' });
      navigate(`/doctor/consultations/${id}`);
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to accept case', type: 'error' });
    } finally { setAccepting(null); }
  };

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  const critical = queue.filter(c => c.riskLevel === 'CRITICAL');
  const high     = queue.filter(c => c.riskLevel === 'HIGH');
  const medium   = queue.filter(c => c.riskLevel === 'MEDIUM');

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="section-label text-indigo-400">Teleconsultation</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Priority Queue</h1>
          <p className="text-slate-400 text-sm">
            {queue.length} case{queue.length !== 1 ? 's' : ''} · auto-refreshes every 30s
          </p>
        </div>
        <Button variant="secondary" onClick={() => { setLoading(true); fetch(); }}>
          <RefreshCw size={15} /> Refresh
        </Button>
      </div>

      {queue.length === 0 ? (
        <EmptyState
          icon={<CheckCircle size={48} className="text-teal-400" />}
          title="Queue is clear"
          sub="All high-risk cases have been attended to."
        />
      ) : (
        <>
          <QueueSection title="🚨 Critical" color="critical" items={critical}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
          <QueueSection title="⚠ High Risk" color="high"     items={high}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
          <QueueSection title="⚡ Medium Risk" color="medium" items={medium}
            onAccept={handleAccept} accepting={accepting} navigate={navigate} />
        </>
      )}

      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}

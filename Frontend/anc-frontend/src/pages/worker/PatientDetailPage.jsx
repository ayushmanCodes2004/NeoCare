import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPatient } from '../../api/patientApi';
import { getPatientVisits } from '../../api/visitApi';
import { getPatientConsults } from '../../api/consultationApi';
import RiskBadge from '../../components/ui/RiskBadge';
import Button from '../../components/ui/Button';
import Spinner from '../../components/ui/Spinner';
import { Plus, Phone, MapPin, Droplets, Calendar, ChevronRight, Video, Stethoscope } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

function InfoPill({ icon: Icon, label, value }) {
  if (!value) return null;
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon size={14} className="text-slate-500 flex-shrink-0" />
      <span className="text-slate-400 text-xs">{label}:</span>
      <span className="text-slate-200 font-medium">{value}</span>
    </div>
  );
}

export default function PatientDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient,   setPatient]   = useState(null);
  const [visits,    setVisits]    = useState([]);
  const [consults,  setConsults]  = useState([]);
  const [loading,   setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([getPatient(id), getPatientVisits(id), getPatientConsults(id)])
      .then(([p, v, c]) => { setPatient(p); setVisits(v); setConsults(c); })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!patient) return <div className="p-8 text-slate-400">Patient not found.</div>;

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="section-label">Patient Profile</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">{patient.fullName}</h1>
          <div className="flex flex-wrap gap-4 mt-2">
            <InfoPill icon={Phone}   label="Phone"  value={patient.phone} />
            <InfoPill icon={MapPin}  label="Village" value={[patient.village, patient.district].filter(Boolean).join(', ')} />
            <InfoPill icon={Droplets} label="Blood Group" value={patient.bloodGroup} />
            <InfoPill icon={Calendar} label="LMP" value={patient.lmpDate && format(new Date(patient.lmpDate), 'dd MMM yyyy')} />
            <InfoPill icon={Calendar} label="EDD" value={patient.eddDate && format(new Date(patient.eddDate), 'dd MMM yyyy')} />
          </div>
        </div>
        <Button onClick={() => navigate(`/visits/new/${patient.patientId}`)}>
          <Plus size={16} /> New Visit
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Visit history */}
        <div className="lg:col-span-2">
          <p className="section-label mb-3">Visit History ({visits.length})</p>
          {visits.length === 0 ? (
            <div className="glass-card p-10 text-center">
              <p className="text-slate-500 text-sm mb-3">No visits recorded yet</p>
              <Button onClick={() => navigate(`/visits/new/${patient.patientId}`)} variant="outline">
                <Plus size={16} /> Record First Visit
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {visits.map(v => (
                <button
                  key={v.id}
                  onClick={() => navigate(`/visits/${v.id}`)}
                  className="w-full glass-card p-4 flex items-center justify-between hover:border-teal-500/30 transition-all group text-left"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <RiskBadge level={v.riskLevel} />
                      <span className={`text-xs px-2 py-0.5 rounded-full font-mono
                        ${v.status === 'AI_ANALYZED' ? 'text-teal-400 bg-teal-400/10'
                        : v.status === 'AI_FAILED'   ? 'text-risk-high bg-risk-high/10'
                        : 'text-slate-400 bg-white/5'}`}>
                        {v.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">
                      {v.createdAt && format(new Date(v.createdAt), 'dd MMM yyyy, HH:mm')}
                      {v.confidence && ` · Confidence ${Math.round(v.confidence * 100)}%`}
                    </p>
                    {v.detectedRisks?.length > 0 && (
                      <p className="text-xs text-slate-600 mt-1 truncate max-w-md">
                        {v.detectedRisks.slice(0, 3).join(' · ')}
                      </p>
                    )}
                  </div>
                  <ChevronRight size={16} className="text-slate-600 group-hover:text-teal-400 transition-colors flex-shrink-0" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Consultations */}
        <div>
          <p className="section-label mb-3">Doctor Consultations ({consults.length})</p>
          {consults.length === 0 ? (
            <div className="glass-card p-6 text-center">
              <Stethoscope size={24} className="text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500 text-xs">No consultations yet</p>
              <p className="text-slate-600 text-xs mt-1">Consultations are auto-created when a visit is flagged as high risk</p>
            </div>
          ) : (
            <div className="space-y-2">
              {consults.map(c => (
                <div key={c.consultationId} className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <RiskBadge level={c.riskLevel} />
                    <span className={`text-xs font-mono px-2 py-0.5 rounded-full
                      ${c.status === 'COMPLETED'   ? 'text-teal-400 bg-teal-400/10'
                      : c.status === 'IN_PROGRESS' ? 'text-risk-medium bg-risk-medium/10 animate-pulse'
                      : c.status === 'ACCEPTED'    ? 'text-indigo-400 bg-indigo-400/10'
                      : 'text-slate-400 bg-white/5'}`}>
                      {c.status}
                    </span>
                  </div>
                  {c.doctorName && (
                    <p className="text-xs text-slate-400">Dr. {c.doctorName}</p>
                  )}
                  {c.status === 'IN_PROGRESS' && c.workerToken && c.roomUrl && (
                    <a
                      href={`${c.roomUrl}?t=${c.workerToken}`}
                      target="_blank" rel="noreferrer"
                      className="mt-2 flex items-center justify-center gap-1.5 w-full text-xs py-2 rounded-lg bg-teal-500/20 text-teal-300 border border-teal-500/30 hover:bg-teal-500/30 transition-colors"
                    >
                      <Video size={12} /> Join Video Call
                    </a>
                  )}
                  {c.status === 'COMPLETED' && c.actionPlan && (
                    <div className="mt-2 p-2 rounded-lg bg-white/5 text-xs text-slate-300">
                      <p className="font-mono text-teal-400 mb-1">Action Plan:</p>
                      <p className="leading-relaxed">{c.actionPlan}</p>
                    </div>
                  )}
                  <p className="text-[10px] text-slate-600 mt-2">
                    {c.createdAt && formatDistanceToNow(new Date(c.createdAt), { addSuffix: true })}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

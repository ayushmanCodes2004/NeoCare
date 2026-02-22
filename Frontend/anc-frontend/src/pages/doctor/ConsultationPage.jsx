import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { getConsult, startCall, completeConsult } from '../../api/consultationApi';
import VideoRoom from '../../components/video/VideoRoom';
import RiskBadge from '../../components/ui/RiskBadge';
import ConfidenceBar from '../../components/visits/ConfidenceBar';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Spinner from '../../components/ui/Spinner';
import Toast from '../../components/ui/Toast';
import { ArrowLeft, Video, VideoOff, CheckCircle, AlertTriangle, Phone, MapPin, User } from 'lucide-react';

function DataCard({ title, icon: Icon, children }) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-2 section-label mb-3">
        {Icon && <Icon size={13} />} {title}
      </div>
      {children}
    </div>
  );
}

function InfoRow({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex justify-between items-start py-1.5 border-b border-white/5 last:border-0">
      <span className="text-xs text-slate-500 flex-shrink-0 w-28">{label}</span>
      <span className="text-sm text-slate-200 text-right font-medium">{value}</span>
    </div>
  );
}

export default function ConsultationPage() {
  const { id }   = useParams();
  const navigate = useNavigate();
  const [consult,    setConsult]    = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [callBusy,   setCallBusy]   = useState(false);
  const [inCall,     setInCall]     = useState(false);
  const [toast,      setToast]      = useState(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const reload = () => getConsult(id).then(d => {
    setConsult(d);
    if (d.status === 'IN_PROGRESS' && d.roomUrl) setInCall(true);
  }).finally(() => setLoading(false));

  useEffect(() => { reload(); }, [id]);

  const handleStartCall = async () => {
    setCallBusy(true);
    try {
      const updated = await startCall(id);
      setConsult(updated);
      setInCall(true);
      setToast({ msg: 'Video room created. Worker has been notified.', type: 'success' });
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to start call', type: 'error' });
    } finally { setCallBusy(false); }
  };

  const handleComplete = async (notes) => {
    try {
      await completeConsult(id, notes);
      setToast({ msg: 'Consultation completed successfully', type: 'success' });
      setTimeout(() => navigate('/doctor/queue'), 1500);
    } catch (e) {
      setToast({ msg: e.response?.data?.message || 'Failed to complete', type: 'error' });
    }
  };

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;
  if (!consult) return <div className="p-8 text-slate-400">Consultation not found.</div>;

  const c = consult;
  const isCompleted = c.status === 'COMPLETED';

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <button onClick={() => navigate('/doctor/queue')}
            className="flex items-center gap-1 text-xs text-slate-500 hover:text-indigo-400 mb-2 transition-colors">
            <ArrowLeft size={14} /> Back to Queue
          </button>
          <div className="flex items-center gap-3">
            <RiskBadge level={c.riskLevel} large />
            <h1 className="font-display text-2xl font-bold text-slate-100">
              {c.patientName || 'Patient'}
            </h1>
            <span className={`text-xs px-3 py-1 rounded-full font-mono font-semibold
              ${isCompleted ? 'text-teal-400 bg-teal-400/10'
              : c.status === 'IN_PROGRESS' ? 'text-risk-medium bg-risk-medium/10 animate-pulse'
              : 'text-indigo-400 bg-indigo-400/10'}`}>
              {c.status}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT: Patient + Risk info */}
        <div className="space-y-4">
          <DataCard title="Patient Details" icon={User}>
            <InfoRow label="Name"            value={c.patientName} />
            <InfoRow label="Age"             value={c.patientAge ? `${c.patientAge} years` : null} />
            <InfoRow label="Gestational Age" value={c.gestationalWeeks ? `${c.gestationalWeeks} weeks` : null} />
            <InfoRow label="Blood Group"     value={c.bloodGroup} />
            <InfoRow label="Phone"           value={c.patientPhone} />
            <InfoRow label="Location"        value={[c.village, c.district].filter(Boolean).join(', ')} />
          </DataCard>

          <DataCard title="AI Risk Assessment" icon={AlertTriangle}>
            <div className="mb-3">
              <ConfidenceBar value={c.confidence} />
            </div>
            {c.detectedRisks?.length > 0 && (
              <div className="mb-3">
                <p className="text-xs text-slate-500 mb-1.5">Detected Risk Factors:</p>
                <div className="flex flex-wrap gap-1.5">
                  {c.detectedRisks.map((r, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-risk-critical/10 text-risk-critical border border-risk-critical/20">
                      {r}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {c.explanation && (
              <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                <p className="text-xs text-slate-400 leading-relaxed">{c.explanation}</p>
              </div>
            )}
            {c.recommendation && (
              <div className="mt-3 p-3 rounded-xl bg-teal-500/10 border border-teal-500/20">
                <p className="text-xs font-mono text-teal-400 mb-1">RECOMMENDATION</p>
                <p className="text-sm text-teal-200 font-medium">{c.recommendation}</p>
              </div>
            )}
          </DataCard>

          <DataCard title="ANC Worker" icon={Phone}>
            <InfoRow label="Worker"        value={c.workerName} />
            <InfoRow label="Phone"         value={c.workerPhone} />
            <InfoRow label="Health Center" value={c.healthCenter} />
          </DataCard>
        </div>

        {/* RIGHT: Video + Notes */}
        <div className="space-y-4">

          {/* Video call */}
          <DataCard title="Video Teleconsultation" icon={Video}>
            {isCompleted ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <CheckCircle size={40} className="text-teal-400 mb-3" />
                <p className="text-slate-300 font-medium">Consultation Completed</p>
                <p className="text-xs text-slate-500 mt-1">Call session has ended</p>
              </div>
            ) : inCall && c.roomUrl && c.doctorToken ? (
              <VideoRoom
                roomUrl={c.roomUrl}
                token={c.doctorToken}
                onLeave={() => setInCall(false)}
              />
            ) : (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <div className="h-16 w-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4">
                  {c.status === 'ACCEPTED' ? (
                    <Video size={28} className="text-indigo-400" />
                  ) : (
                    <VideoOff size={28} className="text-slate-500" />
                  )}
                </div>
                <p className="text-slate-300 text-sm font-medium mb-1">
                  {c.status === 'ACCEPTED' ? 'Ready to start' : 'Accept case to begin'}
                </p>
                <p className="text-xs text-slate-500 mb-4">
                  {c.status === 'ACCEPTED'
                    ? 'Worker will receive a notification to join'
                    : 'Go to queue and accept this case first'}
                </p>
                <Button
                  onClick={handleStartCall}
                  loading={callBusy}
                  disabled={c.status !== 'ACCEPTED'}
                  className="bg-indigo-500 hover:bg-indigo-400 text-white"
                >
                  <Video size={16} /> Start Video Call
                </Button>
              </div>
            )}
          </DataCard>

          {/* Notes form or completed notes */}
          {isCompleted ? (
            <DataCard title="Completed Notes" icon={CheckCircle}>
              {c.doctorNotes && (
                <div className="mb-3">
                  <p className="text-xs text-slate-500 mb-1">Clinical Notes</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{c.doctorNotes}</p>
                </div>
              )}
              {c.diagnosis && (
                <div className="mb-3">
                  <p className="text-xs text-slate-500 mb-1">Diagnosis</p>
                  <p className="text-sm text-slate-300 font-medium">{c.diagnosis}</p>
                </div>
              )}
              {c.actionPlan && (
                <div className="p-3 rounded-xl bg-teal-500/10 border border-teal-500/20">
                  <p className="text-xs font-mono text-teal-400 mb-1">ACTION PLAN</p>
                  <p className="text-sm text-teal-200 whitespace-pre-line">{c.actionPlan}</p>
                </div>
              )}
            </DataCard>
          ) : (
            <DataCard title="Consultation Notes" icon={CheckCircle}>
              <form onSubmit={handleSubmit(handleComplete)} noValidate>
                <Input label="Clinical Notes *" type="textarea" rows={3}
                  placeholder="Describe findings, patient condition, interventions..."
                  error={errors.doctorNotes?.message}
                  {...register('doctorNotes', { required: 'Clinical notes are required' })} />
                <Input label="Diagnosis" type="textarea" rows={2}
                  placeholder="e.g. Severe Pre-eclampsia with anaemia"
                  {...register('diagnosis')} />
                <Input label="Action Plan *" type="textarea" rows={3}
                  placeholder={"1. Immediate referral to CEmOC\n2. IV MgSO4\n3. Blood transfusion"}
                  error={errors.actionPlan?.message}
                  {...register('actionPlan', { required: 'Action plan is required' })} />
                <Button type="submit" loading={isSubmitting}
                  className="w-full mt-2 bg-teal-500 hover:bg-teal-400 text-navy-950 font-semibold">
                  <CheckCircle size={16} /> Complete Consultation
                </Button>
              </form>
            </DataCard>
          )}
        </div>
      </div>

      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}

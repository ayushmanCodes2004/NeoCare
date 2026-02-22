import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getConsultation, acceptConsultation, startCall, completeConsultation } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Loader2, CheckCircle, Video, AlertTriangle, Stethoscope, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const ConsultationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [consultation, setConsultation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showComplete, setShowComplete] = useState(false);
  const [notes, setNotes] = useState({ doctorNotes: '', diagnosis: '', actionPlan: '' });

  useEffect(() => {
    if (!id) return;
    getConsultation(id).then(r => setConsultation(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  const handleAccept = async () => {
    if (!id) return;
    setActionLoading(true);
    try { const { data } = await acceptConsultation(id); setConsultation((p: any) => ({ ...p, ...data, status: 'ACCEPTED' })); } catch {} finally { setActionLoading(false); }
  };

  const handleStartCall = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await startCall(id);
      setConsultation((p: any) => ({ ...p, status: 'IN_PROGRESS' }));
      // Navigate to video call page
      navigate(`/doctor/consultations/${id}/video`);
    } catch {} finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!id) return;
    setActionLoading(true);
    try { await completeConsultation(id, notes); setShowComplete(false); setConsultation((p: any) => ({ ...p, status: 'COMPLETED', ...notes })); } catch {} finally { setActionLoading(false); }
  };

  if (loading) return <AppLayout><div className="text-center py-12 text-muted-foreground">Loading...</div></AppLayout>;
  if (!consultation) return <AppLayout><div className="text-center py-12 text-muted-foreground">Consultation not found.</div></AppLayout>;

  const c = consultation;

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto animate-fade-in">
        <Link to="/doctor/consultations" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />Back to Queue
        </Link>

        {/* Patient & Risk Info */}
        <div className="bg-card rounded-lg border shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-foreground">{c.patientName}, {c.patientAge}y</h1>
              <p className="text-muted-foreground text-sm">{c.gestationalAge} · {c.district} · {c.patientPhone}</p>
            </div>
            <RiskBadge level={c.riskLevel} className="text-sm px-3 py-1" />
          </div>

          <div className="bg-muted rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-foreground">Risk Score</span>
              <span className="text-xl font-bold text-foreground">{c.riskScore}/100</span>
            </div>
            <div className="w-full h-2 bg-border rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${c.riskScore}%`, backgroundColor: c.riskLevel === 'LOW' ? 'hsl(var(--risk-low))' : c.riskLevel === 'MEDIUM' ? 'hsl(var(--risk-medium))' : c.riskLevel === 'HIGH' ? 'hsl(var(--risk-high))' : 'hsl(var(--risk-critical))' }} />
            </div>
          </div>

          {c.riskFactors?.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5 text-risk-high" />Risk Factors</h3>
              <ul className="space-y-1">{c.riskFactors.map((f: string, i: number) => <li key={i} className="text-sm text-foreground bg-muted rounded-md p-2">{f}</li>)}</ul>
            </div>
          )}

          {c.aiRecommendations?.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-1"><Stethoscope className="h-3.5 w-3.5 text-primary" />AI Recommendations</h3>
              <ul className="space-y-1">{c.aiRecommendations.map((r: string, i: number) => <li key={i} className="text-sm text-foreground bg-muted rounded-md p-2">{r}</li>)}</ul>
            </div>
          )}

          {c.clinicalSummary && <p className="text-sm text-muted-foreground italic">{c.clinicalSummary}</p>}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {c.status === 'PENDING' && (
            <Button onClick={handleAccept} disabled={actionLoading}>
              {actionLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle className="mr-2 h-4 w-4" />}
              Accept Consultation
            </Button>
          )}
          {c.status === 'ACCEPTED' && (
            <Button onClick={handleStartCall} disabled={actionLoading}>
              {actionLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Video className="mr-2 h-4 w-4" />}
              Start Video Call
            </Button>
          )}
          {c.status === 'IN_PROGRESS' && (
            <Button onClick={() => setShowComplete(true)}>
              <CheckCircle className="mr-2 h-4 w-4" />Complete Consultation
            </Button>
          )}
          {c.status === 'COMPLETED' && (
            <div className="bg-card rounded-lg border shadow-sm p-6 w-full">
              <h3 className="font-semibold text-foreground mb-3">Consultation Notes</h3>
              <div className="space-y-3 text-sm">
                <div><p className="text-muted-foreground">Doctor Notes</p><p className="text-foreground">{c.doctorNotes}</p></div>
                <div><p className="text-muted-foreground">Diagnosis</p><p className="text-foreground">{c.diagnosis}</p></div>
                <div><p className="text-muted-foreground">Action Plan</p><p className="text-foreground">{c.actionPlan}</p></div>
              </div>
            </div>
          )}
        </div>

        {/* Complete Dialog */}
        <Dialog open={showComplete} onOpenChange={setShowComplete}>
          <DialogContent>
            <DialogHeader><DialogTitle>Complete Consultation</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2"><Label>Doctor Notes *</Label><Textarea value={notes.doctorNotes} onChange={e => setNotes(p => ({ ...p, doctorNotes: e.target.value }))} placeholder="Examination findings..." /></div>
              <div className="space-y-2"><Label>Diagnosis *</Label><Input value={notes.diagnosis} onChange={e => setNotes(p => ({ ...p, diagnosis: e.target.value }))} placeholder="Clinical diagnosis..." /></div>
              <div className="space-y-2"><Label>Action Plan *</Label><Textarea value={notes.actionPlan} onChange={e => setNotes(p => ({ ...p, actionPlan: e.target.value }))} placeholder="Follow-up plan..." /></div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowComplete(false)}>Cancel</Button>
              <Button onClick={handleComplete} disabled={actionLoading || !notes.doctorNotes || !notes.diagnosis || !notes.actionPlan}>
                {actionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Complete
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
};

export default ConsultationDetail;

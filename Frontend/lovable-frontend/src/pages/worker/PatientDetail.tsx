import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPatient, getPatientVisits } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';
import { Button } from '@/components/ui/button';
import { ClipboardPlus, ArrowLeft } from 'lucide-react';

const PatientDetail = () => {
  const { id } = useParams();
  const [patient, setPatient] = useState<any>(null);
  const [visits, setVisits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    Promise.all([getPatient(id), getPatientVisits(id)])
      .then(([p, v]) => { setPatient(p.data); setVisits(v.data || []); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  // Format date properly
  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'N/A';
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
      });
    } catch {
      return 'N/A';
    }
  };

  // Format status for display
  const formatStatus = (status: string) => {
    if (!status) return '';
    return status.replace(/_/g, ' ').toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) return <AppLayout><div className="text-center py-12 text-muted-foreground">Loading...</div></AppLayout>;
  if (!patient) return <AppLayout><div className="text-center py-12 text-muted-foreground">Patient not found.</div></AppLayout>;

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <Link to="/worker/patients" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />Back to Patients
        </Link>

        <div className="bg-card rounded-lg border shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">{patient.fullName}</h1>
              <p className="text-muted-foreground mt-1">Age {patient.age} · {patient.phone}</p>
            </div>
            <Link to={`/worker/visits/new?patientId=${id}`}>
              <Button><ClipboardPlus className="mr-2 h-4 w-4" />New Visit</Button>
            </Link>
          </div>
          <div className="grid sm:grid-cols-3 gap-4 mt-6 text-sm">
            {[
              ['Village', patient.village], ['District', patient.district], ['Blood Group', patient.bloodGroup],
              ['LMP Date', patient.lmpDate], ['EDD Date', patient.eddDate], ['Address', patient.address],
            ].map(([l, v]) => (
              <div key={l as string}><p className="text-muted-foreground">{l}</p><p className="font-medium text-foreground">{v || '—'}</p></div>
            ))}
          </div>
        </div>

        <div className="bg-card rounded-lg border shadow-sm">
          <div className="p-4 border-b"><h2 className="font-semibold text-foreground">Visit History</h2></div>
          {visits.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">No visits recorded yet.</div>
          ) : (
            <div className="divide-y">
              {visits.map((v: any) => (
                <Link key={v.visitId} to={`/worker/visits/${v.visitId}/result`} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div>
                    <p className="font-medium text-foreground">Visit on {formatDate(v.savedAt)}</p>
                    <p className="text-sm text-muted-foreground">{formatStatus(v.status)}</p>
                  </div>
                  {v.riskAssessment && <RiskBadge level={v.riskAssessment.risk_level} />}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default PatientDetail;

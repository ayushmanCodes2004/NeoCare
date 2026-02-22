import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDoctorHistory } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';

const DoctorHistory = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDoctorHistory().then(r => setHistory(r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground mb-6">Consultation History</h1>
        {loading ? (
          <div className="text-center py-12 text-muted-foreground">Loading...</div>
        ) : history.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">No consultation history.</div>
        ) : (
          <div className="grid gap-3">
            {history.map((c: any) => (
              <Link key={c.consultationId} to={`/doctor/consultations/${c.consultationId}`} className="bg-card rounded-lg border p-4 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-foreground">{c.patientName}</p>
                    <p className="text-sm text-muted-foreground mt-0.5">{c.diagnosis || 'No diagnosis'}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <RiskBadge level={c.riskLevel} />
                    <span className="text-xs text-muted-foreground">{c.completedAt ? new Date(c.completedAt).toLocaleDateString() : c.status}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default DoctorHistory;

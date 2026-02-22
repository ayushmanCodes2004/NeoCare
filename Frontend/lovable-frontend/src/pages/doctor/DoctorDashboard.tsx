import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getConsultationQueue } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';
import { Button } from '@/components/ui/button';
import { ClipboardList, Clock, CheckCircle } from 'lucide-react';

const DoctorDashboard = () => {
  const { user } = useAuth();
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getConsultationQueue().then(r => setQueue(r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const pending = queue.filter(c => c.status === 'PENDING').length;
  const stats = [
    { label: 'Pending', value: pending, icon: ClipboardList, color: 'text-warning' },
    { label: 'In Progress', value: queue.filter(c => c.status === 'IN_PROGRESS').length, icon: Clock, color: 'text-info' },
    { label: 'Completed', value: queue.filter(c => c.status === 'COMPLETED').length, icon: CheckCircle, color: 'text-success' },
  ];

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">Welcome, {user?.fullName || 'Doctor'}</h1>
          <p className="text-muted-foreground mt-1">Your consultation overview and priority queue.</p>
        </div>

        <div className="grid sm:grid-cols-3 gap-4 mb-8">
          {stats.map(s => (
            <div key={s.label} className="bg-card rounded-lg border p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{s.label}</p>
                  <p className="text-3xl font-bold text-foreground mt-1">{loading ? '—' : s.value}</p>
                </div>
                <s.icon className={`h-8 w-8 ${s.color} opacity-70`} />
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3 mb-8">
          <Link to="/doctor/consultations"><Button><ClipboardList className="mr-2 h-4 w-4" />View Full Queue</Button></Link>
        </div>

        <div className="bg-card rounded-lg border shadow-sm">
          <div className="p-4 border-b"><h2 className="font-semibold text-foreground">Priority Queue</h2></div>
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Loading...</div>
          ) : queue.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">No consultations in queue.</div>
          ) : (
            <div className="divide-y">
              {queue.slice(0, 5).map((c: any) => (
                <Link key={c.consultationId} to={`/doctor/consultations/${c.consultationId}`} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div>
                    <p className="font-medium text-foreground">{c.patientName}, {c.patientAge}y</p>
                    <p className="text-sm text-muted-foreground">{c.gestationalAge} · {c.district}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <RiskBadge level={c.riskLevel} />
                    <span className="text-xs text-muted-foreground capitalize px-2 py-1 rounded-md bg-muted">{c.status}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default DoctorDashboard;

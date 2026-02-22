import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getPatients } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Users, Activity, AlertTriangle, UserPlus, Eye } from 'lucide-react';

const WorkerDashboard = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPatients().then(r => setPatients(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const stats = [
    { label: 'Total Patients', value: patients.length, icon: Users, color: 'text-primary' },
    { label: 'Recent Visits', value: patients.length > 0 ? Math.min(patients.length, 5) : 0, icon: Activity, color: 'text-info' },
    { label: 'High Risk', value: 0, icon: AlertTriangle, color: 'text-risk-high' },
  ];

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">Welcome back, {user?.fullName || 'Worker'}</h1>
          <p className="text-muted-foreground mt-1">Here's an overview of your patients and activities.</p>
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
          <Link to="/worker/patients/new">
            <Button><UserPlus className="mr-2 h-4 w-4" />Register Patient</Button>
          </Link>
          <Link to="/worker/patients">
            <Button variant="outline"><Eye className="mr-2 h-4 w-4" />View All Patients</Button>
          </Link>
        </div>

        <div className="bg-card rounded-lg border shadow-sm">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-foreground">Recent Patients</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Loading...</div>
          ) : patients.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">No patients registered yet. Start by adding a new patient.</div>
          ) : (
            <div className="divide-y">
              {patients.slice(0, 5).map((p: any) => (
                <Link key={p.patientId} to={`/worker/patients/${p.patientId}`} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                  <div>
                    <p className="font-medium text-foreground">{p.fullName}</p>
                    <p className="text-sm text-muted-foreground">Age {p.age} · {p.village} · {p.bloodGroup}</p>
                  </div>
                  <span className="text-sm text-muted-foreground">EDD: {p.eddDate}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default WorkerDashboard;

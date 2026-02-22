import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getConsultationQueue } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import RiskBadge from '@/components/RiskBadge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const statuses = ['ALL', 'PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED'];

const ConsultationQueue = () => {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('ALL');

  useEffect(() => {
    getConsultationQueue().then(r => setQueue(r.data || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const filtered = tab === 'ALL' ? queue : queue.filter(c => c.status === tab);

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground mb-6">Consultation Queue</h1>

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="mb-6">
            {statuses.map(s => <TabsTrigger key={s} value={s} className="capitalize">{s.replace('_', ' ').toLowerCase()}</TabsTrigger>)}
          </TabsList>

          <TabsContent value={tab}>
            {loading ? (
              <div className="text-center py-12 text-muted-foreground">Loading...</div>
            ) : filtered.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No consultations found.</div>
            ) : (
              <div className="grid gap-3">
                {filtered.map((c: any) => (
                  <Link key={c.consultationId} to={`/doctor/consultations/${c.consultationId}`} className="bg-card rounded-lg border p-4 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-foreground">{c.patientName}, {c.patientAge}y</p>
                        <p className="text-sm text-muted-foreground mt-0.5">{c.gestationalAge} · {c.district} · Score: {c.riskScore}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <RiskBadge level={c.riskLevel} />
                        <span className="text-xs text-muted-foreground capitalize px-2 py-1 rounded-md bg-muted">{c.status?.replace('_', ' ').toLowerCase()}</span>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">Created: {new Date(c.createdAt).toLocaleString()}</p>
                  </Link>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
};

export default ConsultationQueue;

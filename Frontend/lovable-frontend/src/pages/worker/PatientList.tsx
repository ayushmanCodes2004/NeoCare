import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPatients } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { UserPlus, Search } from 'lucide-react';

const PatientList = () => {
  const [patients, setPatients] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPatients().then(r => setPatients(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const filtered = patients.filter(p =>
    p.fullName?.toLowerCase().includes(search.toLowerCase()) ||
    p.phone?.includes(search)
  );

  return (
    <AppLayout>
      <div className="animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-foreground">Patients</h1>
          <Link to="/worker/patients/new">
            <Button><UserPlus className="mr-2 h-4 w-4" />Add Patient</Button>
          </Link>
        </div>

        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input className="pl-10" placeholder="Search by name or phone..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>

        {loading ? (
          <div className="text-center py-12 text-muted-foreground">Loading patients...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            {search ? 'No patients match your search.' : 'No patients registered yet.'}
          </div>
        ) : (
          <div className="grid gap-3">
            {filtered.map((p: any) => (
              <Link key={p.patientId} to={`/worker/patients/${p.patientId}`} className="bg-card rounded-lg border p-4 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between">
                <div>
                  <p className="font-semibold text-foreground">{p.fullName}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Age {p.age} · {p.phone} · {p.village} · {p.bloodGroup}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">EDD</p>
                  <p className="text-sm font-medium text-foreground">{p.eddDate}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default PatientList;

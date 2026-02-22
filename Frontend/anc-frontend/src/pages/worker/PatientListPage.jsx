import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPatients } from '../../api/patientApi';
import Spinner from '../../components/ui/Spinner';
import Button from '../../components/ui/Button';
import EmptyState from '../../components/ui/EmptyState';
import { Plus, Search, ChevronRight, MapPin, Phone, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export default function PatientListPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [query,    setQuery]    = useState('');

  useEffect(() => {
    getPatients().then(d => { setPatients(d); setFiltered(d); }).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const q = query.toLowerCase();
    setFiltered(patients.filter(p =>
      p.fullName?.toLowerCase().includes(q) ||
      p.phone?.includes(q) ||
      p.village?.toLowerCase().includes(q)
    ));
  }, [query, patients]);

  if (loading) return <div className="flex h-full items-center justify-center"><Spinner lg /></div>;

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="section-label">Registry</p>
          <h1 className="font-display text-2xl font-bold text-slate-100">Patients</h1>
          <p className="text-slate-400 text-sm">{patients.length} registered</p>
        </div>
        <Button onClick={() => navigate('/patients/new')}>
          <Plus size={16} /> New Patient
        </Button>
      </div>

      {/* Search */}
      <div className="relative mb-5">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search by name, phone, village..."
          className="w-full pl-10 pr-4 py-2.5 bg-navy-800 border border-white/10 rounded-xl text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-teal-500/50"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon="🤱"
          title={query ? 'No patients match your search' : 'No patients registered yet'}
          sub={query ? 'Try a different search term' : 'Click "New Patient" to register your first patient'}
          action={!query && <Button onClick={() => navigate('/patients/new')}><Plus size={16} /> Register Patient</Button>}
        />
      ) : (
        <div className="space-y-2">
          {filtered.map(p => (
            <button
              key={p.patientId}
              onClick={() => navigate(`/patients/${p.patientId}`)}
              className="w-full glass-card p-4 flex items-center justify-between hover:border-teal-500/30 transition-all group text-left"
            >
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-teal-500/20 border border-teal-500/30 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-teal-300">{p.fullName?.[0]?.toUpperCase()}</span>
                </div>
                <div>
                  <p className="font-medium text-slate-100">{p.fullName}</p>
                  <div className="flex items-center gap-3 mt-0.5">
                    {p.phone && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <Phone size={10} /> {p.phone}
                      </span>
                    )}
                    {p.village && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <MapPin size={10} /> {p.village}
                      </span>
                    )}
                    {p.age && (
                      <span className="text-xs text-slate-500">Age {p.age}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {p.lmpDate && (
                  <span className="flex items-center gap-1 text-xs text-slate-500">
                    <Calendar size={10} /> {format(new Date(p.lmpDate), 'dd MMM yyyy')}
                  </span>
                )}
                <ChevronRight size={16} className="text-slate-600 group-hover:text-teal-400 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

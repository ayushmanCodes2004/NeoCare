import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createPatient } from '@/services/api';
import AppLayout from '@/components/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';

const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];

const PatientCreate = () => {
  const [form, setForm] = useState({ fullName: '', phone: '', age: '', address: '', village: '', district: '', lmpDate: '', eddDate: '', bloodGroup: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await createPatient({ ...form, age: parseInt(form.age) });
      navigate(`/worker/patients/${data.patientId}`);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to register patient');
    } finally { setLoading(false); }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto animate-fade-in">
        <h1 className="text-2xl font-bold text-foreground mb-6">Register New Patient</h1>
        <form onSubmit={handleSubmit} className="bg-card rounded-lg border shadow-sm p-6 space-y-4">
          {error && <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">{error}</div>}
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2"><Label>Full Name</Label><Input placeholder="Lakshmi Devi" value={form.fullName} onChange={set('fullName')} required /></div>
            <div className="space-y-2"><Label>Phone</Label><Input placeholder="9123456789" value={form.phone} onChange={set('phone')} required /></div>
            <div className="space-y-2"><Label>Age</Label><Input type="number" placeholder="26" value={form.age} onChange={set('age')} required /></div>
            <div className="space-y-2">
              <Label>Blood Group</Label>
              <Select value={form.bloodGroup} onValueChange={v => setForm(p => ({ ...p, bloodGroup: v }))}>
                <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>{bloodGroups.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-2 space-y-2"><Label>Address</Label><Input placeholder="123 Main Street" value={form.address} onChange={set('address')} required /></div>
            <div className="space-y-2"><Label>Village</Label><Input placeholder="Koramangala" value={form.village} onChange={set('village')} required /></div>
            <div className="space-y-2"><Label>District</Label><Input placeholder="Bangalore Urban" value={form.district} onChange={set('district')} required /></div>
            <div className="space-y-2"><Label>LMP Date</Label><Input type="date" value={form.lmpDate} onChange={set('lmpDate')} required /></div>
            <div className="space-y-2"><Label>EDD Date</Label><Input type="date" value={form.eddDate} onChange={set('eddDate')} required /></div>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Register Patient
          </Button>
        </form>
      </div>
    </AppLayout>
  );
};

export default PatientCreate;

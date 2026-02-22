import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { doctorSignup } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heart, Loader2 } from 'lucide-react';

const DoctorSignup = () => {
  const [form, setForm] = useState({ fullName: '', phone: '', email: '', password: '', specialization: '', hospital: '', district: '', registrationNo: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!/^[6-9]\d{9}$/.test(form.phone)) { setError('Phone must be 10 digits starting with 6-9'); return; }
    if (form.password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setLoading(true);
    try {
      const { data } = await doctorSignup(form);
      login(data.token, 'DOCTOR', data);
      navigate('/doctor/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Signup failed');
    } finally { setLoading(false); }
  };

  const fields = [
    { key: 'fullName', label: 'Full Name', placeholder: 'Dr. Rajesh Kumar' },
    { key: 'phone', label: 'Phone Number', placeholder: '9988776655' },
    { key: 'email', label: 'Email', placeholder: 'rajesh@hospital.in', type: 'email' },
    { key: 'password', label: 'Password', placeholder: '••••••••', type: 'password' },
    { key: 'specialization', label: 'Specialization', placeholder: 'Obstetrics & Gynaecology' },
    { key: 'hospital', label: 'Hospital', placeholder: 'District Hospital' },
    { key: 'district', label: 'District', placeholder: 'Bangalore Urban' },
    { key: 'registrationNo', label: 'Registration No.', placeholder: 'KA-12345' },
  ];

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <Heart className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">NeoSure</span>
          </Link>
          <h1 className="text-xl font-semibold text-foreground">Doctor Registration</h1>
        </div>
        <form onSubmit={handleSubmit} className="bg-card rounded-lg border shadow-sm p-6 space-y-4">
          {error && <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">{error}</div>}
          {fields.map(f => (
            <div key={f.key} className="space-y-2">
              <Label>{f.label}</Label>
              <Input type={f.type || 'text'} placeholder={f.placeholder} value={(form as any)[f.key]} onChange={set(f.key)} required />
            </div>
          ))}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Account
          </Button>
          <p className="text-sm text-center text-muted-foreground">
            Already have an account? <Link to="/doctor/login" className="text-primary font-medium hover:underline">Sign In</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default DoctorSignup;

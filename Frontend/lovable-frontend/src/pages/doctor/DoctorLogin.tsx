import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { doctorLogin } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heart, Loader2 } from 'lucide-react';

const DoctorLogin = () => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!/^[6-9]\d{9}$/.test(phone)) { setError('Phone must be 10 digits starting with 6-9'); return; }
    setLoading(true);
    try {
      const { data } = await doctorLogin({ phone, password });
      login(data.token, 'DOCTOR', data);
      navigate('/doctor/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Invalid credentials');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <Heart className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold text-foreground">NeoSure</span>
          </Link>
          <h1 className="text-xl font-semibold text-foreground">Doctor Sign In</h1>
          <p className="text-sm text-muted-foreground mt-1">Access consultation queue & patient reviews</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-card rounded-lg border shadow-sm p-6 space-y-4">
          {error && <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">{error}</div>}
          <div className="space-y-2">
            <Label>Phone Number</Label>
            <Input placeholder="9988776655" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Password</Label>
            <Input type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Sign In
          </Button>
          <p className="text-sm text-center text-muted-foreground">
            Don't have an account? <Link to="/doctor/signup" className="text-primary font-medium hover:underline">Sign Up</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default DoctorLogin;

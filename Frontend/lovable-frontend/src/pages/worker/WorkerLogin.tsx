import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { workerLogin } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Heart, Loader2 } from 'lucide-react';

const WorkerLogin = () => {
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
    if (password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setLoading(true);
    try {
      const { data } = await workerLogin({ phone, password });
      login(data.token, 'WORKER', data);
      navigate('/worker/dashboard');
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
          <h1 className="text-xl font-semibold text-foreground">Health Worker Sign In</h1>
          <p className="text-sm text-muted-foreground mt-1">Access your patient management dashboard</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-card rounded-lg border shadow-sm p-6 space-y-4">
          {error && <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md">{error}</div>}
          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <Input id="phone" placeholder="9876543210" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Sign In
          </Button>
          <p className="text-sm text-center text-muted-foreground">
            Don't have an account? <Link to="/worker/signup" className="text-primary font-medium hover:underline">Sign Up</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default WorkerLogin;

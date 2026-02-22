import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Activity, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const { login }  = useAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async ({ phone, password }) => {
    setErr('');
    try { await login(phone, password); navigate('/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Login failed. Check your credentials.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex">
      {/* Left panel */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-navy-900 via-navy-800 to-teal-900/30 flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-teal-500 flex items-center justify-center">
            <Activity size={20} className="text-navy-950" />
          </div>
          <span className="font-display text-xl font-bold text-slate-100">ANC Portal</span>
        </div>
        <div>
          <blockquote className="text-3xl font-display font-bold text-slate-100 leading-snug mb-4">
            Maternal health<br />intelligence at<br />every level of care.
          </blockquote>
          <p className="text-slate-400 text-sm">
            AI-powered risk assessment for Antenatal Care workers —<br />connecting field workers with specialists in real-time.
          </p>
        </div>
        <div className="flex gap-6 text-xs font-mono text-slate-500">
          <span>CRITICAL ALERTS</span>
          <span>REAL-TIME TRIAGE</span>
          <span>VIDEO CONSULT</span>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm animate-fade-in">
          <div className="mb-8">
            <p className="section-label">ANC Worker Portal</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Sign in</h1>
            <p className="text-slate-400 text-sm mt-1">Enter your phone number and password</p>
          </div>

          {err && (
            <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
              <AlertCircle size={16} className="flex-shrink-0" /> {err}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <Input
              label="Phone Number"
              type="tel"
              placeholder="9876543210"
              error={errors.phone?.message}
              {...register('phone', {
                required: 'Phone number is required',
                pattern: { value: /^[6-9]\d{9}$/, message: 'Enter a valid 10-digit mobile number' },
              })}
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register('password', { required: 'Password is required' })}
            />
            <Button type="submit" loading={isSubmitting} className="w-full mt-2" size="lg">
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-6">
            New worker?{' '}
            <Link to="/signup" className="text-teal-400 hover:text-teal-300 font-medium">
              Create account
            </Link>
          </p>
          <p className="text-center text-xs text-slate-600 mt-3">
            Doctor?{' '}
            <Link to="/doctor/login" className="text-slate-400 hover:text-slate-300">
              Doctor portal →
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { Activity, AlertCircle } from 'lucide-react';

export default function SignupPage() {
  const { signup } = useAuth();
  const navigate   = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    setErr('');
    try { await signup(data); navigate('/dashboard'); }
    catch (e) { setErr(e.response?.data?.message || 'Signup failed. Please try again.'); }
  };

  return (
    <div className="min-h-screen bg-navy-950 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-fade-in">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="h-10 w-10 rounded-xl bg-teal-500 flex items-center justify-center">
            <Activity size={20} className="text-navy-950" />
          </div>
          <div>
            <p className="section-label">Worker Registration</p>
            <h1 className="font-display text-2xl font-bold text-slate-100">Create account</h1>
          </div>
        </div>

        {err && (
          <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
            <AlertCircle size={16} className="flex-shrink-0" /> {err}
          </div>
        )}

        <div className="glass-card p-6">
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="grid grid-cols-2 gap-x-4">
              <div className="col-span-2">
                <Input label="Full Name *" placeholder="Anjali Devi"
                  error={errors.fullName?.message}
                  {...register('fullName', { required: 'Full name is required' })} />
              </div>
              <Input label="Phone *" type="tel" placeholder="9876543210"
                error={errors.phone?.message}
                {...register('phone', {
                  required: 'Phone is required',
                  pattern: { value: /^[6-9]\d{9}$/, message: 'Invalid number' },
                })} />
              <Input label="Email" type="email" placeholder="anjali@phc.in"
                {...register('email')} />
              <div className="col-span-2">
                <Input label="Password *" type="password" placeholder="Min. 8 characters"
                  error={errors.password?.message}
                  {...register('password', { required: true, minLength: { value: 8, message: 'Min 8 chars' } })} />
              </div>
              <Input label="Health Center *" placeholder="PHC Angondhalli"
                error={errors.healthCenter?.message}
                {...register('healthCenter', { required: 'Health center is required' })} />
              <Input label="District *" placeholder="Bangalore Rural"
                error={errors.district?.message}
                {...register('district', { required: 'District is required' })} />
            </div>
            <Button type="submit" loading={isSubmitting} className="w-full mt-2" size="lg">
              Create Account
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-slate-500 mt-5">
          Already registered?{' '}
          <Link to="/login" className="text-teal-400 hover:text-teal-300 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

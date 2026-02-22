import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { createPatient } from '../../api/patientApi';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import { AlertCircle, UserPlus } from 'lucide-react';

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function PatientCreatePage() {
  const navigate = useNavigate();
  const [err, setErr] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  const onSubmit = async (data) => {
    setErr('');
    try {
      const patient = await createPatient({
        ...data,
        age: data.age ? Number(data.age) : null,
      });
      navigate(`/patients/${patient.patientId}`);
    } catch (e) {
      setErr(e.response?.data?.message || 'Failed to register patient');
    }
  };

  return (
    <div className="p-8 max-w-2xl animate-fade-in">
      <div className="mb-6">
        <p className="section-label">Registration</p>
        <h1 className="font-display text-2xl font-bold text-slate-100 flex items-center gap-2">
          <UserPlus size={24} className="text-teal-400" /> New Patient
        </h1>
      </div>

      {err && (
        <div className="flex items-center gap-2 mb-5 p-3 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-sm">
          <AlertCircle size={16} /> {err}
        </div>
      )}

      <div className="glass-card p-6">
        <form onSubmit={handleSubmit(onSubmit)} noValidate>

          {/* Personal info */}
          <p className="section-label mb-3">Personal Information</p>
          <div className="grid grid-cols-2 gap-x-4">
            <div className="col-span-2">
              <Input label="Full Name *" placeholder="Meena Kumari"
                error={errors.fullName?.message}
                {...register('fullName', { required: 'Full name is required' })} />
            </div>
            <Input label="Phone" type="tel" placeholder="9123456789" {...register('phone')} />
            <Input label="Age" type="number" placeholder="24"
              {...register('age', { min: { value: 10, message: 'Invalid age' }, max: { value: 60, message: 'Invalid age' } })}
              error={errors.age?.message}
            />
          </div>

          <div className="grid grid-cols-2 gap-x-4">
            <div className="mb-4">
              <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-1.5">Blood Group</label>
              <select className="w-full px-4 py-2.5 rounded-xl bg-navy-800 border border-white/10 text-slate-100 text-sm focus:outline-none focus:border-teal-500/50"
                {...register('bloodGroup')}>
                <option value="">— Select —</option>
                {BLOOD_GROUPS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <Input label="Village" placeholder="Hebbal" {...register('village')} />
          </div>

          <div className="grid grid-cols-2 gap-x-4">
            <Input label="District" placeholder="Bangalore Rural" {...register('district')} />
            <Input label="Address" placeholder="123 Main St" {...register('address')} />
          </div>

          {/* Pregnancy info */}
          <p className="section-label mb-3 mt-2">Pregnancy Details</p>
          <div className="grid grid-cols-2 gap-x-4">
            <Input label="LMP Date" type="date"
              hint="Last Menstrual Period"
              {...register('lmpDate')} />
            <Input label="EDD Date" type="date"
              hint="Expected Due Date"
              {...register('eddDate')} />
          </div>

          <div className="flex gap-3 mt-4 pt-4 border-t border-white/10">
            <Button type="submit" loading={isSubmitting} size="lg">
              Register Patient
            </Button>
            <Button variant="secondary" onClick={() => navigate('/patients')} size="lg">
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

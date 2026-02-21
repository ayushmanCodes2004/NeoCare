import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { createPatient } from '../api/patientApi';
import { Calendar, User, Phone, MapPin, Home, Droplet } from 'lucide-react';

/**
 * Patient registration page with NeoSure professional design
 */
export default function PatientCreatePage() {
  const navigate = useNavigate();
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setApiError(null);
    setLoading(true);
    try {
      const patient = await createPatient(data);
      navigate(`/patients/${patient.patientId}`);
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Failed to register patient'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="neosure-dashboard">
      {/* Header */}
      <div className="mb-10">
        <h2 className="header-title mb-2">Register New Patient</h2>
        <p className="header-subtitle">Enter patient demographic and pregnancy details</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <div className="card-white">
            {apiError && (
              <div className="spotlight-alert mb-6">
                <p>{apiError}</p>
                <button 
                  onClick={() => setApiError(null)}
                  className="ml-auto text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-8">
              {/* Personal Information */}
              <div className="space-y-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <User className="text-primary" size={20} />
                  Personal Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold flex items-center gap-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      placeholder="Meena Kumari"
                      className={`form-input-neosure ${errors.fullName ? 'error' : ''}`}
                      {...register('fullName', {
                        required: 'Full name is required',
                      })}
                    />
                    {errors.fullName && (
                      <span className="form-error-neosure">{errors.fullName.message}</span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold flex items-center gap-2">
                      <Phone size={14} className="text-primary" />
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      placeholder="9123456789"
                      className={`form-input-neosure ${errors.phone ? 'error' : ''}`}
                      {...register('phone', {
                        required: 'Phone number is required',
                        pattern: {
                          value: /^[6-9]\d{9}$/,
                          message: 'Enter a valid 10-digit mobile number',
                        },
                      })}
                    />
                    {errors.phone && (
                      <span className="form-error-neosure">{errors.phone.message}</span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold">Age</label>
                    <input
                      type="number"
                      placeholder="24"
                      className={`form-input-neosure ${errors.age ? 'error' : ''}`}
                      {...register('age', {
                        required: 'Age is required',
                        min: { value: 15, message: 'Age must be at least 15' },
                        max: { value: 50, message: 'Age must be less than 50' },
                      })}
                    />
                    {errors.age && (
                      <span className="form-error-neosure">{errors.age.message}</span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold flex items-center gap-2">
                      <Droplet size={14} className="text-primary" />
                      Blood Group
                    </label>
                    <input
                      type="text"
                      placeholder="B+ (Optional)"
                      className="form-input-neosure"
                      {...register('bloodGroup')}
                    />
                  </div>
                </div>
              </div>

              <hr className="border-border-light" />

              {/* Address Information */}
              <div className="space-y-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <MapPin className="text-primary" size={20} />
                  Address Information
                </h3>

                <div className="grid grid-cols-1 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold flex items-center gap-2">
                      <Home size={14} className="text-primary" />
                      Address
                    </label>
                    <input
                      type="text"
                      placeholder="123 Main Street, Hebbal"
                      className={`form-input-neosure ${errors.address ? 'error' : ''}`}
                      {...register('address', {
                        required: 'Address is required',
                      })}
                    />
                    {errors.address && (
                      <span className="form-error-neosure">{errors.address.message}</span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-semibold">Village</label>
                      <input
                        type="text"
                        placeholder="Hebbal"
                        className={`form-input-neosure ${errors.village ? 'error' : ''}`}
                        {...register('village', {
                          required: 'Village is required',
                        })}
                      />
                      {errors.village && (
                        <span className="form-error-neosure">{errors.village.message}</span>
                      )}
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-semibold">District</label>
                      <input
                        type="text"
                        placeholder="Bangalore Rural"
                        className={`form-input-neosure ${errors.district ? 'error' : ''}`}
                        {...register('district', {
                          required: 'District is required',
                        })}
                      />
                      {errors.district && (
                        <span className="form-error-neosure">{errors.district.message}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <hr className="border-border-light" />

              {/* Pregnancy Details */}
              <div className="space-y-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <Calendar className="text-primary" size={20} />
                  Pregnancy Details
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold">
                      LMP Date <span className="text-xs font-normal opacity-60">(Last Menstrual Period)</span>
                    </label>
                    <input
                      type="date"
                      className={`form-input-neosure ${errors.lmpDate ? 'error' : ''}`}
                      {...register('lmpDate', {
                        required: 'LMP date is required',
                      })}
                    />
                    {errors.lmpDate && (
                      <span className="form-error-neosure">{errors.lmpDate.message}</span>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-semibold">
                      EDD <span className="text-xs font-normal opacity-60">(Expected Delivery Date)</span>
                    </label>
                    <input
                      type="date"
                      className={`form-input-neosure ${errors.eddDate ? 'error' : ''}`}
                      {...register('eddDate', {
                        required: 'EDD is required',
                      })}
                    />
                    {errors.eddDate && (
                      <span className="form-error-neosure">{errors.eddDate.message}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => navigate('/patients')}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary-alert"
                >
                  {loading ? 'Registering...' : 'Register Patient'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Sidebar - Guidelines */}
        <div className="space-y-6">
          <div className="card-primary">
            <h3 className="card-subtitle-white mb-3">Registration Guidelines</h3>
            <ul className="space-y-4">
              <li className="flex gap-3 text-sm leading-relaxed text-white opacity-90">
                <span className="flex-shrink-0">✓</span>
                <span>Ensure all patient details are accurate for proper tracking</span>
              </li>
              <li className="flex gap-3 text-sm leading-relaxed text-white opacity-90">
                <span className="flex-shrink-0">✓</span>
                <span>LMP date is crucial for calculating gestation weeks</span>
              </li>
              <li className="flex gap-3 text-sm leading-relaxed text-white opacity-90">
                <span className="flex-shrink-0">✓</span>
                <span>Phone number will be used for follow-up reminders</span>
              </li>
            </ul>
          </div>

          <div className="card-white">
            <h4 className="card-subtitle mb-4">Next Steps</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary font-bold text-xs">
                  1
                </div>
                <p className="text-stone-600">Register patient with basic details</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary font-bold text-xs">
                  2
                </div>
                <p className="text-stone-600">Schedule first ANC visit</p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary font-bold text-xs">
                  3
                </div>
                <p className="text-stone-600">Record vitals and get risk assessment</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

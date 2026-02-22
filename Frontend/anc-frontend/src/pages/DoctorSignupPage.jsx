import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import axios from 'axios';
import '../styles/auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/**
 * Doctor Signup page — calls POST /api/auth/doctor/signup
 * Styled to match NeoSure landing page theme
 */
export default function DoctorSignupPage() {
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
      // Map frontend field names to backend expected names
      const payload = {
        fullName: data.fullName,
        phone: data.phone,
        email: data.email,
        password: data.password,
        specialization: data.specialization,
        hospital: data.hospital,
        district: data.district,
        registrationNo: data.licenseNumber // Backend expects registrationNo
      };
      
      const response = await axios.post(`${API_BASE_URL}/api/doctor/auth/signup`, payload);
      
      // Store token and user info
      localStorage.setItem('anc_token', response.data.token);
      localStorage.setItem('anc_role', 'DOCTOR');
      localStorage.setItem('anc_user', JSON.stringify({
        doctorId: response.data.doctorId,
        fullName: response.data.fullName,
        email: response.data.email,
        phone: response.data.phone,
        specialization: data.specialization,
        hospital: response.data.hospital,
        district: response.data.district
      }));
      console.log('Signup successful! Redirecting to doctor dashboard...');
      console.log('Stored data:', {
        token: !!response.data.token,
        role: localStorage.getItem('anc_role'),
        user: localStorage.getItem('anc_user')
      });
      
      // Force navigation to doctor dashboard
      window.location.href = '/doctor/dashboard';
    } catch (err) {
      setApiError(
        err.response?.data?.message || 'Signup failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-dots-tl"></div>
      <div className="auth-dots-br"></div>

      <Link to="/" className="auth-back-link">
        ← Back to Home
      </Link>

      <div className="auth-card wide">
        {/* Header */}
        <div className="auth-header">
          <div className="auth-logo">
            <div className="auth-logo-mark">🌸</div>
            <span className="auth-logo-text">NeoSure</span>
          </div>
          <h1 className="auth-title">Join as Doctor</h1>
          <p className="auth-subtitle">Register to provide expert consultations</p>
        </div>

        {/* Error Alert */}
        {apiError && (
          <div className="auth-alert error">
            <span className="auth-alert-icon">⚠️</span>
            <span>{apiError}</span>
            <button 
              className="auth-alert-close" 
              onClick={() => setApiError(null)}
              aria-label="Close"
            >
              ×
            </button>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="auth-form grid">
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              placeholder="Dr. Priya Sharma"
              className={`form-input ${errors.fullName ? 'error' : ''}`}
              {...register('fullName', {
                required: 'Full name is required',
              })}
            />
            {errors.fullName && (
              <span className="form-error">
                ⚠ {errors.fullName.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              placeholder="doctor@hospital.com"
              className={`form-input ${errors.email ? 'error' : ''}`}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Enter a valid email address',
                },
              })}
            />
            {errors.email && (
              <span className="form-error">
                ⚠ {errors.email.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input
              type="tel"
              placeholder="9876543210"
              className={`form-input ${errors.phone ? 'error' : ''}`}
              {...register('phone', {
                required: 'Phone number is required',
                pattern: {
                  value: /^[6-9]\d{9}$/,
                  message: 'Enter a valid 10-digit mobile number',
                },
              })}
            />
            {errors.phone && (
              <span className="form-error">
                ⚠ {errors.phone.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              className={`form-input ${errors.password ? 'error' : ''}`}
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
              })}
            />
            {errors.password && (
              <span className="form-error">
                ⚠ {errors.password.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Specialization</label>
            <select
              className={`form-input ${errors.specialization ? 'error' : ''}`}
              {...register('specialization', {
                required: 'Specialization is required',
              })}
            >
              <option value="">Select specialization</option>
              <option value="Gynecologist">Gynecologist</option>
              <option value="Obstetrician">Obstetrician</option>
              <option value="Maternal-Fetal Medicine">Maternal-Fetal Medicine</option>
              <option value="General Physician">General Physician</option>
            </select>
            {errors.specialization && (
              <span className="form-error">
                ⚠ {errors.specialization.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Medical License Number</label>
            <input
              type="text"
              placeholder="MCI-12345"
              className={`form-input ${errors.licenseNumber ? 'error' : ''}`}
              {...register('licenseNumber', {
                required: 'License number is required',
              })}
            />
            {errors.licenseNumber && (
              <span className="form-error">
                ⚠ {errors.licenseNumber.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">Hospital/Clinic</label>
            <input
              type="text"
              placeholder="City General Hospital"
              className={`form-input ${errors.hospital ? 'error' : ''}`}
              {...register('hospital', {
                required: 'Hospital/Clinic is required',
              })}
            />
            {errors.hospital && (
              <span className="form-error">
                ⚠ {errors.hospital.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label">District</label>
            <input
              type="text"
              placeholder="Bangalore Urban"
              className={`form-input ${errors.district ? 'error' : ''}`}
              {...register('district', {
                required: 'District is required',
              })}
            />
            {errors.district && (
              <span className="form-error">
                ⚠ {errors.district.message}
              </span>
            )}
          </div>

          <div className="form-group full-width">
            <button
              type="submit"
              disabled={loading}
              className={`auth-submit-btn ${loading ? 'loading' : ''}`}
            >
              {!loading && 'Create Account'}
            </button>
          </div>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          Already have an account?{' '}
          <Link to="/doctor/login">Sign in here</Link>
        </div>
      </div>
    </div>
  );
}
